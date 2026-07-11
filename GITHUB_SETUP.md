# Pushing this project to GitHub

One-time setup to get `autonomous-robot` onto GitHub. Run these in a terminal.

## Prerequisites
- Git installed: check with `git --version` (if missing, install from https://git-scm.com).
- A GitHub account.

## Step 1 — create an empty repo on GitHub
Go to https://github.com/new and:
- Repository name: `autonomous-robot`
- Description: "Building toward an AI-driven autonomous robot, one working machine at a time."
- Public or Private: your call.
- **Do NOT** check "Add a README" / .gitignore / license — this project already has them.
- Click **Create repository**. Leave that page open; you'll copy the URL.

## Step 2 — initialize and push (run in the project folder)
Open a terminal in this folder:
`C:\Users\ultra\OneDrive\Documents\Engineering Projects\autonomous-robot`

(In File Explorer, right-click the folder > "Open in Terminal", or `cd` to it.)

Then run:

```bash
git init
git add .
git commit -m "Initial project scaffold: roadmap, docs, hardware BOM, structure"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/autonomous-robot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username (the URL is shown on the page from Step 1).

## Step 3 — future updates
After that first push, saving new work to GitHub is just:

```bash
git add .
git commit -m "describe what changed"
git push
```

## Notes
- If `git push` asks you to sign in, use a **Personal Access Token** as the password (GitHub > Settings > Developer settings > Personal access tokens). Never paste tokens into a chat.
- OneDrive already backs this folder up to the cloud; GitHub adds version history + a public/portfolio home for the code.
- Once the GitHub connector is fully authorized in Claude, I can handle commits and pushes for you directly.
