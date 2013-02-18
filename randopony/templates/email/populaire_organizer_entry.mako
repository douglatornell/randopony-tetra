${rider.full_name | n} <${rider.email}> has pre-registered for the ${populaire.short_name}.  Zher name should appear along with the other pre-registered riders on the list at <${pop_page_url}>, in the spreadsheet at <${rider_list_url}>, and in the rider's email address list at <${rider_emails}>.

Zhe should have received a confirmation email that appears to have come from your email address so that zhe can contact you directly, if necessary.

%if ',' in populaire.distance:
${rider} has indicated that zhe is planning to ride the ${rider.distance} km distance.
%endif

This is an auto-generated email. If you are having problems with the RandoPony system please send email to <${admin_email}>.

Sincerely,

The Rando Pony
