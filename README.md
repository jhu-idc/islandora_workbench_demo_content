# Islandora_Workbench Demo Content
This content is intended to be used with [islandora_workbench](https://github.com/mjordan/islandora_workbench) to demonstrate the functionality of the tool.  This can be used to test the tool, or to create a sandbox environment for testing and development.

## Steps to use this content
Overview of the steps to use this content:
1. Clone islandora_workbench repo
1. Clone this repo inside of that directory
1. Edit config file
1. Build the docker container
1. Check the config (_optional_)
1. Run the docker container to create the content

### Detailed steps
1. Clone https://github.com/mjordan/islandora_workbench
1. Change directory into the islandora_workbench directory (`cd islandora_workbench`) 
1. Clone this repo inside of that directory (`git clone https://github.com/DonRichards/islandora_workbench_demo_content`)
1. Open __example_content.yml__ and change the line with _"nopassword"_ to the password in Drupal or to contents of _isle-dc/secrets/live/DRUPAL_DEFAULT_ACCOUNT_PASSWORD_.
1. Open __example_content.yml__ and change the line with input directory to include the absolute path for _demo_content_files/_ where it's mounted inside of the container. `input_dir: /workbench/islandora_workbench_demo_content/demo_content_files`. See notes below for more information.
1. Then run the docker build command from the parent directory __islandora_workbench__: `docker build -t workbench-docker .`
1. __(Optional)__ Check the config `docker run -it --rm --network="host" -v $(pwd):/workbench --name my-running-workbench workbench-docker bash -lc "cd /workbench ; python setup.py install ; ./workbench --config /workbench/islandora_workbench_demo_content/example_content.yml --check"`
1. To create content start the container process `docker run -it --rm --network="host" -v $(pwd):/workbench --name my-running-workbench workbench-docker bash -lc "cd /workbench ; python setup.py install ; ./workbench --config /workbench/islandora_workbench_demo_content/example_content.yml"`

### Notes:

In the config file, the `input_dir` is set to `/workbench/islandora_workbench_demo_content/demo_content_files` because that is the absolute path to the directory when the container is running.  If you are running the workbench on your local machine, you will need to change the `input_dir` to the absolute path to the directory on your local machine.

## ... ROLLBACK IS CURRENTLY NOT WORKING WITH THIS DEMO CONTENT ...
### To rollback the demo content
 Check the config `docker run -it --rm --network="host" -v $(pwd):/workbench --name my-running-workbench workbench-docker bash -lc "cd /workbench ; python setup.py install ; ./workbench --config /workbench/rollback.yml"`


#### Workaround
If you want to rollback the content, you will need to manually delete the content from Drupal.  The content should be removed in the following order:
Files -> Media -> Nodes
```shell
# !!!!! WARNING !!!!!
# This will remove ALL media and files from the site

# Remove all files
docker-compose -f ../docker-compose.yml exec -T drupal bash -lc "drush entity:delete file"

# Remove all media
docker-compose -f ../docker-compose.yml exec -T drupal bash -lc "drush entity:delete media"

# Remove all nodes
docker-compose -f ../docker-compose.yml exec -T drupal bash -lc "drush entity:delete node $(tail -n +2 islandora_workbench_demo_content/demo_content_files/rollback.csv | sed 'H;1h;$!d;x;y/\n/,/')"

```

A more cautious solution would be to remove the content in the reverse order that it was created.  This would be a little more complicated to implement, but would be safer.
Here's a script that will do that but should be used with caution and not on a production site.
[Github Gist: rollback_workaround.sh](https://gist.github.com/DonRichards/f23d9240fcf40cbe8005df093b4acaa2#file-rollback_workaround-sh)

### TL;DR
```shell
git clone https://github.com/mjordan/islandora_workbench
cd islandora_workbench
git clone https://github.com/DonRichards/islandora_workbench_demo_content
sed -i.bak "s/^nopassword.*/password\: $(cat ../secrets/live/DRUPAL_DEFAULT_ACCOUNT_PASSWORD) /g" islandora_workbench_demo_content/example_content.yml
sed -i.bak "s|^input_dir.*|input_dir\: /workbench/islandora_workbench_demo_content/demo_content_files|g" islandora_workbench_demo_content/example_content.yml
docker build -t workbench-docker .
docker run -it --rm --network="host" -v $(pwd):/workbench --name my-running-workbench workbench-docker bash -lc "cd /workbench ; python setup.py install ; ./workbench --config /workbench/islandora_workbench_demo_content/example_content.yml"
```

## TO DO
- [ ] Add setup.py install to Dockerfile
- [X] Make Alternative rollback option
- [ ] Fix rollback functionality
