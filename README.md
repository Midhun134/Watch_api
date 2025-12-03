github action workflow steps taken ->
tried lot of yaml files but didn't work out as i got errors mostly in the ssh authorisation and copying files into gcp vm section, first the error was private key not being seen by the gcp
then private key is in .ppk format because it was generated from putty key generator so it needs a passphrase to unlock the private file and for that itself it took an hour or 2 because i tried 
with atleast 2 yaml files since the gcp server is not recognising the passphrase and tried with coding it normal and "uses" which are like kind of a decorator. next i created a new private and
public key pair by sshing into gcp server and the public key was uploaded into ~/.ssh something file and private key was kept as a secret in github actions.i thought of just sticking with 1 yaml and then try to fix errors one by one on that, in the yaml file, the setup ssh key, the private ssh key was deployed into ~/.ssh/deploy_key and at first i was scp for copying files from github into the gcp server because it is compatible with ssh and much easier to setup but the problem is that it deletes the complete previous repository and then downloads the new one onto the gcp server which we have to manually setup the virtual environment so i found a better option which is rsync that just updates only the changed files and is used mainly by developers. Next i was using nohup to run my django api 24/7 but it is not recommended for production so i switched to gunicorn.
Test gunicorn (replace 'your_project' with actual folder name)
gunicorn your_project.wsgi:application --bind 0.0.0.0:8000
Then i created a systemmd service file at /etc/systemd/system/django.service to add some of the process/requirments. these are the commands that i ran to run the server
#Reload systemd
sudo systemctl daemon-reload
#Enable service to start on boot
sudo systemctl enable django.service
#Start the service
sudo systemctl start django.service
the github workflow finally ran successfully but there was one problem the api call was giving 400 bad requests so i tried running gunicorn using the port 8000 but it says the port is already in use and i checked it using systemctl status and there were 3 workers running and the reason the api call was not pinging is because in the settings.py the allowed hosts were empty so i put * inside the allowed hosts list to allow all which is not recommended for security and then restarted the server using sudo systemctl restart django.service and now everything works properly.
Made a new change where before in the yaml file to restart django server it was sudo systemctl restart django.service now changed to sudo systemctl reload django.service and to Reload systemd manager configuration if you changed the service file use sudo systemctl daemon-reload

