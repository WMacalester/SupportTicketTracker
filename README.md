# Project Aims
The aim of this project is to create a support ticket service using flask. This support ticket service should have a means of keeping track of all submitted tickets, as well as feedback on whether the ticket is being addressed or if it has been completed. 

There should be two types of users - general users who submit tickets and admins who are processing tickets. General users should be able to submit new tickets alongside viewing old tickets and their statuses. Admins should have access to all submitted tickets which are open, and only they should see it if they have picked up the ticket (assuming multiple admins). Completed tickets should go in an archive directory for posterity. 

Admins should have to login through an authentication system. Admins should also have the ability to add further admins, and the ability to change their password if they so choose. 

This shall be further updated depending on how far down the rabbit hole I decide to go - this is my first attempt at building a web based browser after all. This initial code shall be heavily based off the pyflask tutorial as I get to grips with it, as the tutorial creates a working blog website which can be transposed to a support ticket system. Wish me luck!


# Finishing Original Aims 

I have now reached the original goals for what I wanted to learn with this project. Testing was implemented, yielding test coverage ~98 %.  

Some brief examples of the different views and permissions between the user and admin roles:

![Example Window](/images/Example_1_user.png)
1) The user index view correctly shows only the current user's tickets. They have the option to submit a new ticket, and to edit a previous ticket. There is a ticket status that informs the user whether the ticket has been picked up yet. 

<br /> 

![Example Window](/images/Example_2_user.png)  

2) Within the ticket editing window, they can update their title and descriptions, and re-submit the ticket. There is also an option for deleting the ticket if they wish  

<br /> 

![Example Window](/images/Example_3_admin.png)  
3) The index for an admin is populated by tickets from all users. Admins also have the ability to promote another registered user to admin-level through updateAdminRights link in the top bar.

<br /> 

![Example Window](/images/Example_4_admin.png)  
4) When admins edit a ticket, they are able to update both the ticket status and add comments in a separate field

<br /> 

![Example Window](/images/Example_5_admin.png)  
5) When an admin adds a comment, the comment is presented on the ticket in the index

<br /> 

![Example Window](/images/Example_6_user.png)  
6) The admin comment is then displayed for the user, but may not be edited by the user

<br /> 

Going forward, I may try a design overhaul to make it prettier, but that may be saved for another project. I may also implement a way for admins to filter through available tickets by date, title or author. I may also try to deploy this and see how that goes. 
