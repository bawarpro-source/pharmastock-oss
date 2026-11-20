# Publish to GitHub

Target account: https://github.com/bawarpro-source

1. Sign in to GitHub and create a **public**, empty repository named `pharmastock-oss` (do not pre-add a README, licence or .gitignore).
2. Extract the project ZIP locally and open a terminal in the `pharmastock-oss` directory.
3. Run:

```bash
git init
git add .
git commit -m "Initial open-source inventory reconciliation MVP"
git branch -M main
git remote add origin https://github.com/bawarpro-source/pharmastock-oss.git
git push -u origin main
```

GitHub will require you to authenticate. Do not share passwords or tokens with anyone.

4. Check the GitHub Actions tab for the test workflow and enable it if prompted.
5. Add a concise repository description and topics: `pharmacy`, `inventory`, `python`, `open-source`, `reconciliation`.
6. Confirm all sample data is fictional before making the repository public.

**Note:** Creating this repository does not itself satisfy any third-party programme's open-source contribution criteria.
