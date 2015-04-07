#!/bin/bash
# Purpose: generate config_details data
#
# Author: Chris G.
# Date: 03/30/2015
#
## Start ##

random_choice() {
    field_separator=" "
    the_choice=$(echo $@ | awk -v field=$(($RANDOM % $(echo $@ | awk -F"$field_separator" '{print NF}') + 1)) -F"$field_separator" '{print $field}')
    echo $the_choice
}


current_state=("'Enablement Review'")
current_state+=("'Sales Review'")
current_state+=("'Engineering Review'")
current_state+=("'Support Review'")
current_state+=("'Accepted - In Progress'")
current_state+=("'Completed'")
current_state+=("'Rejected'")


customer_name=("'Bank of America'")
customer_name+=("'Southwest Airlines'")
customer_name+=("'ExxonMobil'")
customer_name+=("'Enron'")
customer_name+=("'Lonerider Brewing'")
customer_name+=("'Best Buy'")
customer_name+=("'Amazon.com'")
customer_name+=("'Starbucks'")
customer_name+=("'Paypal'")
customer_name+=("'State of New York'")
customer_name+=("'NSA'")
customer_name+=("'Royal Bank of Scotland'")
customer_name+=("'RichPeople.com'")
customer_name+=("'MercedesBenz'")
customer_name+=("'General Motors'")
customer_name+=("'Honda Motor Company'")
customer_name+=("'Cisco Systems'")
customer_name+=("'Baltimore Ravens'")
customer_name+=("'National Football League'")

short_term_revenue=("'250000'")
short_term_revenue+=("'1250000'")
short_term_revenue+=("'2250000'")
short_term_revenue+=("'3250000'")
short_term_revenue+=("'500000'")
short_term_revenue+=("'1500000'")
short_term_revenue+=("'2500000'")
short_term_revenue+=("'4500000'")
short_term_revenue+=("'5000000'")
short_term_revenue+=("'188000'")
short_term_revenue+=("'99000'")
short_term_revenue+=("'1000000'")
short_term_revenue+=("'2000000'")
short_term_revenue+=("'3000000'")
short_term_revenue+=("'4000000'")


for x in $(seq 100 299); do
    echo "INSERT INTO objects_enablementrequest (identifier, creation_timestamp, current_state, customer_name, assigned_engineer_id, config_details_id, parent_request, sales_initiator_id, slug, short_term_revenue) VALUES (\"ER-0000${x}\", NOW(), ${current_state[$(random_choice $(seq 0 $((${#current_state[@]}-1))))]}, ${customer_name[$(random_choice $(seq 0 $((${#customer_name[@]}-1))))]}, NULL, $(random_choice $(seq 40 240)), '', $(random_choice 7 9 10), \"er-000${x}\", ${short_term_revenue[$(random_choice $(seq 0 $((${#short_term_revenue[@]}-1))))]});"
done





## End ##
