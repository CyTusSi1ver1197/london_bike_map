{{
    config(
    materialized = 'view'
    )
}}


with source as (
      select * from {{ source('staging', 'journey_bike_trip_2018') }}
),
renamed as (
    select
        {{ adapter.quote("Rental Id") }},
        {{ adapter.quote("Duration") }},
        {{ adapter.quote("Bike Id") }},
        {{ adapter.quote("End Date") }},
        {{ adapter.quote("EndStation Id") }},
        {{ adapter.quote("EndStation Name") }},
        {{ adapter.quote("Start Date") }},
        {{ adapter.quote("StartStation Id") }},
        {{ adapter.quote("StartStation Name") }}

    from source
)
select * from renamed
  