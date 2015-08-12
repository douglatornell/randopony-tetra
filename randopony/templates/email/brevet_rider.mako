You have pre-registered for the BC Randonneurs ${brevet} brevet. Your name should appear on the list at <${brevet_page_url}>.

This is an auto-generated email, but you can reply to it to contact the brevet organizer(s).

You can print out the event waiver form from the club web site <${entry_form_url}>, read it carefully, fill it out, and bring it with you to the start to save time and make the organizers like you even more.

%if rider.member_status is None:
Your name couldn't be found in the club database. You need to be a member of the BC Randonneurs Club to ride this brevet. Please join at <${membership_link}>.

If you think that your are in the club database, it's possible that the pony just made a mistake, being just a bit of software and all. Please accept out humblest pony apologies.
%elif not rider.member_status:
Your BC Randonneurs club membership has expired. Please renew it at <${membership_link}>.
%endif

Have a great ride!
