Org Chart Maker
===============

Overview
--------

This is a web application for creating Organizational Charts (Org Charts).

Running
-------

Use the following to run the application:

``python -m flask run --port 5001``

On Linux, you may have to run the following first::

    mkdir -p instance
    touch instance/config.py

Unit Tests
----------

There are two sets of unit tests:

1. Server tests in the "tests" folder.
2. GUI tests in the "gui-tests" folder.

**Server Tests**

To run the server tests, run the following from the root folder:

``python -m pytest``

**GUI Tests**

To run the GUI tests, first install the Selenium Python framework:

``pip install selenium``

Then install the Chrome Selenium driver. For instructions, see:

https://www.selenium.dev/documentation/webdriver/getting_started/install_drivers/

I recommend downloading the driver, and placing it inside the "gui-tests" folder.

Register the selenium user using the Register page:

* Username: selenium_user
* Password: selenium_password

Run the following from the "gui-tests" folder:

``python -m pytest``
