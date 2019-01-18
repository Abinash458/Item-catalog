Cars-Catalog

Create a Car Brand and Model app where users add, edit, and delete Cars Brand and Cars Models.

Prerequirements

1. Python 2.7
2. Vagrant
3. VirtualBox

How to Run

1. Install VirtualBox and Vagrant.
2. Unzip and place the catalog folder in your Vagrant directory.
3. Lunch Vagrant
	$ Vagrant up
4. Login to Vagrant
	$ Vagrant ssh
5. Change to vagrant sharable directory.
	$ cd /vagrant
6. run the database
	$ python database_setup.py
7. Add some data to the database by running the following command
	$ python moreitems.py
8. Lunch the application
	$ python application.py
9. Open the browser and go to http://localhost:5000

For JSON endpoints

1. Return JSON all Brands
	/brand/JSON/
2. Return JSON of specific Brand Model
	/brand/<int:brand_id>/model/<int:model_id>/JSON/
3. Return JSON of Model
	/brand/<int:brand_id>/model/JSON/
