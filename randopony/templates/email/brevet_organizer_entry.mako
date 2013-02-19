${rider.full_name | n} <${rider.email}> has pre-registered for the ${brevet} brevet.  Zher name should appear along with the other pre-registered riders on the list at <${brevet_page_url}>, in the spreadsheet at <${rider_list_url}>, and in the rider's email address list at <${rider_emails}>.

Zhe should have received a confirmation email that appears to have come from your email address so that zhe can contact you directly, if necessary.

%if rider.member_status is None:
This rider's name could not be found in the club database. They may be a new rider, or the problem might just be a spelling mistake. In any case, they have been give the link to use to join the club. Their membership status will appear as "unknown" on the rider list. Please confirm that they are club members before the start of the brevet.
%elif not rider.member_status:
The club database indicates that this rider's membership has expired. They have been informed, but please confirm that they have renewed before the start of the brevet.
%endif

This is an auto-generated email. If you are having problems with the RandoPony system please send email to <${admin_email}>.

Sincerely,

The Rando Pony
