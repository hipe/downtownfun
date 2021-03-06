from invoke import task


@task
def make_pelican_starter_project(c, path):
    from pho_tasks._make_pelican_starter_project import \
            make_pelican_starter_project as func
    return func(c, path)


@task
def make_pelican_intermediate_directory(c, path, author, timezone):
    from pho_tasks._make_pelican_starter_project import \
            make_pelican_intermediate_directory as func
    return func(c, path, author=author, timezone=timezone)


@task
def copy_sphinx_CSS_over(c, do_base_file_too=False, make_project=None):
    from pho_tasks._copy_sphinx_CSS_over import copy_sphinx_CSS_over as func
    return func(c, do_base_file_too, make_project)


@task
def patch_pelican_for_generate_selected(c):
    from pho_tasks._patch_pelican import \
            patch_pelican_for_generate_selected as func
    return func(c)


@task
def patch_pelican_for_write_selected(c):
    from pho_tasks._patch_pelican import \
            patch_pelican_for_write_selected as func
    return func(c)

# #abstracted
