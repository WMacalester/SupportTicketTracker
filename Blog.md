# Adding in an Admin Role

One of the main functional components missing from the tracker on start was the admin role. The admin role has additional responsibilities to the normal base user class. First lets define the features given to the base user class:

* Creation of a ticket
* Editing of a ticket they have submitted
* View all of the tickets they have submitted

The admin class then has the following extra responibilities:
* Update the status of the ticket - whether the ticket has been picked up or completed
* Add a comment to the ticket to relay information back to the user. 
* View all available tickets 
* Ability to upgrade other users to admins

With this in mind, the first step was to add an identifier to differentiate between users and admins. This was done by addition of a bool for adminRights in the users database, with the first admin created at database initialisation and all registered profiles starting as a user. Admins are able to change the adminRights of other registered users and admins through updateAdminRights, but are unable to edit their own to prevent the case where there are no admins.

The ticket status was then implemented by addition of ticketStatus to the post database, which may be updated by an admin. Next, the views were split between admins and users, with admins seeing all posts and users seeing only their posts. The ticket update view for admins now includes a comment box to reply back to the author of the ticket, and radio buttons to update ticket status. The admin comment box is only visible to a user if there has been a comment made. 