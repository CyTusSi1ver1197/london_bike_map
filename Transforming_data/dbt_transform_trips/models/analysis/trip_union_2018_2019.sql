{{
    config(
        materialized = 'table'
    )
}}

select * from {{ref("staging_journey_bike_trip_2018")}}

union all

select * from {{ref("staging_journey_bike_trip_2019")}}