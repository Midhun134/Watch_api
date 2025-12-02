github action workflow steps taken ->
tried lot of yaml files but didn't work out as i got errors mostly in the ssh authorisation and copying files into gcp vm section, first the error was private key not being seen by the gcp
then private key is in .ppk format because it was generated from putty key generator so it needs a passphrase to unlock the private file and for that itself it took an hour or 2 because i tried 
with atleast 2 yaml files since the gcp server is not recognising the passphrase and tried with coding it normal and "uses" which are like kind of a decorator. next i created a new private and
public key pair by sshing into gcp server and the public key was uploaded into ~/.ssh something file and private key was kept as a secret in github actions.
