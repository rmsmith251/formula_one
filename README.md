# formula_one

Mad thanks to the people running http://ergast.com/mrd/ without whom this would be much more difficult.

This is an application I'm building for evaluating driver performance over multiple seasons and multiple criteria.
I preferred to pull the full image because of the simplicity and pulling all of the data through the image
is significantly faster than calling the API. I may add API functionality in the future to update the database.
In addition, the data should only be updated once a week so it's not like constant access to the API is really necessary.

Built on Python 3.7

``python setup.py``
or running the setup file from within your IDE will download the data, create a database, and load the data into the database. 
I currently don't have a way to update the database that isn't just downloading the entire zip file 
but it doesn't take too long.

The current charts are located in ``app.py`` and there isn't much to it. I'll be mainly adding to that as I go forward.

Yes, I know the .csv files are not removed afterwards. I haven't added that in yet because I like to open the files to 
check the data.

If you have any questions, feel free to shoot me a message. I've only coding for 2.5 months so sorry, it's pretty sloppy.
