# PowerShell 脚本：push-all.ps1
Write-Host "📤 Pushing to GitHub..."
git push phot-lab main

Write-Host "📤 Pushing to Gitee..."
git push gitee main:develop

Write-Host "✅ Done."
