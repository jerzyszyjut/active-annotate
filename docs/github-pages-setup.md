# GitHub Pages Setup Instructions

This project uses GitHub Pages to automatically deploy documentation built with Sphinx.

## Automatic Deployment

The documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main/master branch.

### Setup Steps:

1. **Enable GitHub Pages in your repository settings:**

   - Go to your repository on GitHub
   - Click on "Settings" tab
   - Scroll down to "Pages" section
   - Under "Source", select "GitHub Actions"

2. **The workflow will automatically:**

   - Install Python dependencies using pipenv
   - Build the Sphinx documentation
   - Deploy to GitHub Pages

3. **Access your documentation at:**
   https://jerzyszyjut.github.io/active-annotate/

## Manual Documentation Build

To build documentation locally:

```bash
cd docs
pipenv run make html
```

The built documentation will be in `docs/_build/html/`

## Troubleshooting

- Ensure your repository has GitHub Pages enabled
- Check that the workflow has the necessary permissions
- Verify that Sphinx and all dependencies are properly listed in Pipfile
- Make sure the main/master branch protection rules allow the GitHub Actions bot to push
