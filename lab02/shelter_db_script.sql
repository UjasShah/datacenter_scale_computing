--How many animals of each type have outcomes?
select animal_type, count(animal_id) 
from animal_dim 
group by animal_type;
--Dog	560
--Other	53
--Cat	381
--Bird	3


--How many animals are there with more than 1 outcome?
select animal_id, count(*) as number_of_outcomes
from outcomes_fact
group by animal_id
having count(animal_id)> 1
--In the dataset of a 1000 observations, I see three animals with more than one outcome - A788817, A664941, A725680


--What are the top 5 months of outcomes?
select dd.outcome_month ,count(*) as number_of_outcomes
from outcomes_fact of2 
left join date_dim dd 
on of2.date_id = dd.date_id 
group by dd.outcome_month 
order by number_of_outcomes desc
--The top 5 months are
--month		number_of_outcomes
--8			118
--7			105
--6			103
--10		96
--5			88


--What is the total number of kittens, adults, and seniors, whose outcome is "Adopted"?
--Conversely, among all the cats who were "Adopted", what is the total number percentage of kittens, adults, and seniors?
--creating the 'maturity' column
alter table outcomes_fact add column maturity VARCHAR

update outcomes_fact 
set maturity = 
	case
		when age_on_outcome < 1 then 'kitten'
		when age_on_outcome < 10 then 'adult'
		else 'senior cat'
	end

select maturity, count(distinct animal_id) 
from outcomes_fact
where outcome_type_id = 0
group by maturity

--adult	212
--kitten	258
--senior cat	12
--The answer remains the same for both the questions within 4, as we are looking at numbers here and not percentages.


--For each date, what is the cumulative total of outcomes up to and including this date?
with daily_counts as (
select date_id, count(animal_id) as daily_count
from outcomes_fact
group by date_id
)

select date_id,
sum(daily_count) over (order by date_id) as cumulative_sum
from daily_counts
order by date_id

--first couple rows
--20131003	1
--20131005	2
--20131009	3
--20131012	4
--20131013	5
--20131015	6
--20131018	7