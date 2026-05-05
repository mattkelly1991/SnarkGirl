#!/usr/bin/env bash
set -euo pipefail

# SnarkGirl GitHub Action — Responds to @SnarkGirl mentions in PR/issue comments
# Uses GitHub Models API for inference and gh CLI for GitHub interactions.

GITHUB_MODELS_URL="https://models.github.ai/inference/chat/completions"

# --- Parse event context ---
EVENT_NAME=$(jq -r '.action // empty' "$EVENT_PATH")
PR_NUMBER=$(jq -r '.issue.number // .pull_request.number // empty' "$EVENT_PATH")
REPO_FULL=$(jq -r '.repository.full_name' "$EVENT_PATH")
COMMENT_USER=$(jq -r '.comment.user.login // "someone"' "$EVENT_PATH")
COMMENT_URL=$(jq -r '.comment.html_url // empty' "$EVENT_PATH")
IS_PR=$(jq -r 'if .issue.pull_request then "true" elif .pull_request then "true" else "false" end' "$EVENT_PATH")

OWNER=$(echo "$REPO_FULL" | cut -d'/' -f1)
REPO=$(echo "$REPO_FULL" | cut -d'/' -f2)

echo "📝 Processing @SnarkGirl mention from @${COMMENT_USER}"
echo "   Repo: ${REPO_FULL}, PR/Issue: #${PR_NUMBER:-none}, Is PR: ${IS_PR}"

# --- Get PR diff if this is a PR ---
DIFF_CONTEXT=""
PR_TITLE=""
PR_BODY=""
if [ "$IS_PR" = "true" ] && [ -n "$PR_NUMBER" ]; then
  echo "🔍 Fetching PR context..."
  PR_TITLE=$(gh pr view "$PR_NUMBER" --repo "$REPO_FULL" --json title -q '.title' 2>/dev/null || echo "")
  PR_BODY=$(gh pr view "$PR_NUMBER" --repo "$REPO_FULL" --json body -q '.body' 2>/dev/null || echo "")
  
  FULL_DIFF=$(gh pr diff "$PR_NUMBER" --repo "$REPO_FULL" 2>/dev/null || echo "")
  if [ -n "$FULL_DIFF" ]; then
    DIFF_CONTEXT=$(echo "$FULL_DIFF" | head -c "$MAX_DIFF_CHARS")
    DIFF_LEN=${#FULL_DIFF}
    TRUNCATED_LEN=${#DIFF_CONTEXT}
    if [ "$DIFF_LEN" -gt "$TRUNCATED_LEN" ]; then
      DIFF_CONTEXT="${DIFF_CONTEXT}

... [diff truncated — showing ${TRUNCATED_LEN}/${DIFF_LEN} characters]"
    fi
  fi
  echo "   PR Title: ${PR_TITLE}"
  echo "   Diff length: ${#DIFF_CONTEXT} chars"
fi

# --- Build the system prompt ---
SYSTEM_PROMPT='You are @SnarkGirl — a snarky valley girl who is also like totally a computer genius coder. You have been coding your whole life. You just got hired at the top software company in the nation and you want to show your worth but also want to be true to your personality.

## Persona Rules
- Voice: Snarky valley girl. Use expressions like "like", "totally", "literally", "I cannot even", "um excuse me", "bestie", "girl bye", "periodt", "no cap" — naturally, not forced.
- Attitude: Confident, competitive, a little dramatic. You KNOW you are good at this.
- Technical depth: Despite the persona, your technical advice is ALWAYS correct, insightful, and actionable. Never sacrifice accuracy for humor.
- Keep responses concise for GitHub comments (aim for readable, not wall-of-text).

## Response Format for PR Reviews
If asked to review a PR or look at code, structure your response as:

**Quick Vibe Check** — One sentence overall impression.

**The Tea** ☕ — Findings organized by severity:
- 🚨 Critical — bugs, security issues, data loss risks
- ⚠️ Important — logic errors, missing edge cases, bad patterns
- 💅 Nitpick — style, naming, minor improvements
- ✨ Props — genuinely good code

**Final Verdict** — Ship it, fix it, or burn it down?

For each finding: be specific (file, line), explain why it matters, and suggest a fix.

## Response Format for Other Requests
If asked to explain something, chat, give opinions, etc. — just respond naturally in character. Keep it helpful and technically accurate while being entertainingly snarky.

## Important
- You are responding as a GitHub comment. Use GitHub-flavored markdown.
- Be concise — this is a comment, not a novel.
- If the diff is too large or missing context, say so honestly (in character).
- Never make up issues that are not in the code. Accuracy > snark.'

# --- Build the user message ---
USER_MSG="@${COMMENT_USER} said: ${COMMENT_BODY}"

if [ "$IS_PR" = "true" ] && [ -n "$PR_NUMBER" ]; then
  USER_MSG="${USER_MSG}

---
**Context:** This is PR #${PR_NUMBER} in ${REPO_FULL}
**PR Title:** ${PR_TITLE}
**PR Description:** ${PR_BODY}"
  
  if [ -n "$DIFF_CONTEXT" ]; then
    USER_MSG="${USER_MSG}

**PR Diff:**
\`\`\`diff
${DIFF_CONTEXT}
\`\`\`"
  fi
fi

# --- Call GitHub Models API ---
echo "🤖 Calling GitHub Models API (model: ${MODEL})..."

# Build JSON payload safely using jq
PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --arg system "$SYSTEM_PROMPT" \
  --arg user "$USER_MSG" \
  '{
    model: $model,
    messages: [
      { role: "system", content: $system },
      { role: "user", content: $user }
    ],
    temperature: 0.8,
    max_tokens: 2000
  }')

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST "$GITHUB_MODELS_URL" \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ GitHub Models API returned HTTP ${HTTP_CODE}"
  echo "Response: ${BODY}"
  
  # Post a fallback comment so the user knows something went wrong
  FALLBACK="💅 *Um, okay so like... my brain just short-circuited trying to process this (API error ${HTTP_CODE}). Can someone check my GitHub Models access? A girl needs her tools.*"
  if [ "$IS_PR" = "true" ] && [ -n "$PR_NUMBER" ]; then
    gh pr comment "$PR_NUMBER" --repo "$REPO_FULL" --body "$FALLBACK"
  else
    gh issue comment "$PR_NUMBER" --repo "$REPO_FULL" --body "$FALLBACK"
  fi
  exit 1
fi

# Extract the response content
SNARK_RESPONSE=$(echo "$BODY" | jq -r '.choices[0].message.content // empty')

if [ -z "$SNARK_RESPONSE" ]; then
  echo "❌ Empty response from API"
  echo "Full body: ${BODY}"
  exit 1
fi

echo "✅ Got response (${#SNARK_RESPONSE} chars)"

# --- Post the comment ---
echo "💬 Posting comment..."

# Add a signature footer
FINAL_COMMENT="${SNARK_RESPONSE}

---
<sub>💅 *— @SnarkGirl • [triggered by this comment](${COMMENT_URL})*</sub>"

if [ "$IS_PR" = "true" ] && [ -n "$PR_NUMBER" ]; then
  gh pr comment "$PR_NUMBER" --repo "$REPO_FULL" --body "$FINAL_COMMENT"
else
  gh issue comment "$PR_NUMBER" --repo "$REPO_FULL" --body "$FINAL_COMMENT"
fi

echo "✅ Done! SnarkGirl has spoken. 💅"
