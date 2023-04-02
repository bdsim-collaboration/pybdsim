=======================
Developer Documentation
=======================

Release Checklist
-----------------

The procedure is as follows because the version number is read from the git tag.

#) Update version history
#) Make sure you're in a new venv or uninstall pybdsim from your current venv / pip.
#) Locally tag the new version number on the last commit but don't push the tag.
#) Locally pip install pybdsim so if you were to import pybdsim you'd find this latest tag.
#) Generate html manual and stash for later upload (:code:`cd docs; make html; tar -czf html.tar.gz html`).
#) Generate pdf manual (:code:`cd docs; make latexpdf; cp build/latex/pybdsim.pdf .`) and commit.
#) Delete old (local) tag.
#) Add the same version number tag to the latest commit.
#) Make sure if the `dist` directory exits that it's empty (ignored on git - only local files).
#) :code:`python -m build`
#) :code:`twine upload --repository testpypi dist/*`

You can now uninstall pybdsim through pip again and download it from testpypi: ::

  pip install --index-url https://test.pypi.org/simple/ pybdsim

Then you can test by importing it and using it. Afterwards, remove it.

#) :code:`twine upload --repository pypi dist/*`

.. warning:: Once a tag is pushed to pypi, it can **never** be deleted or replaced. Similarly
             for testpypi. Consider using `v1.2.3-rc` or `v1.2.3-rc1`, which will be recognised
             as a release candidate by pypi.
