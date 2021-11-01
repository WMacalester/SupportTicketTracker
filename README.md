# Project Aims
The aim of this project is to create a support ticket service using flask. This support ticket service should have a means of keeping track of all submitted tickets, as well as feedback on whether the ticket is being addressed or if it has been completed. 

There should be two types of users - general users who submit tickets and admins who are processing tickets. General users should be able to submit new tickets alongside viewing old tickets and their statuses. Admins should have access to all submitted tickets which are open, and only they should see it if they have picked up the ticket (assuming multiple admins). Completed tickets should go in an archive directory for posterity. 

Admins should have to login through an authentication system. Admins should also have the ability to add further admins, and the ability to change their password if they so choose. 

This shall be further updated depending on how far down the rabbit hole I decide to go - this is my first attempt at building a web based browser after all. This initial code shall be heavily based off the pyflask tutorial as I get to grips with it, as the tutorial creates a working blog website which can be transposed to a support ticket system. Wish me luck!