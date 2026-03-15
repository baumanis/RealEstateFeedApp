with t1 as (
select RealEstate.Link, count(RealEstate.Link) as Link_Count from RealEstate
group by RealEstate.Link),


t2 as (

select t1.Link,
RealEstate.Id,
RealEstate.Cena,
RealEstate.Izmers,
RealEstate.Stavs,
RealEstate.SerijaId,
RealEstate.MajasTipsId,
RealEstate.ErtibasId,
RealEstate.TypeOfDeal,
RealEstate.PilsetaId,
RealEstate.RajonsId,
RealEstate.IelaId

from t1 left join RealEstate on t1.Link = RealEstate.Link
where t1.Link_Count > 1


),

t3 as

(

select t2.*,
MIN(Ad.DatumsId) as DatumsId,
Pilseta.Name as City,
Rajons.Name as District,
Iela.Name as Street,
Serija.Name as Series,
MajasTips.Name as BuildingType
from t2
left join Ad on t2.Id = Ad.RealEstateId
left join Pilseta on t2.PilsetaId = Pilseta.Id
left join Rajons on t2.RajonsId = Rajons.Id
left join Iela on t2.IelaId = Iela.Id
left join Serija on t2.SerijaId = Serija.Id
left join MajasTips on t2.MajasTipsId = MajasTips.Id

group by t2.Id



)

select t3.Link, 
Datums.StudyDate,
t3.Id,
t3.Cena as Price,
t3.Izmers as Size,
t3.Stavs as Flr,
t3.ErtibasId,
t3.Series,
t3.BuildingType,
t3.City,
t3.District,
t3.Street
from t3 left join Datums on t3.DatumsId = Datums.Id
order by t3.Link, t3.DatumsId