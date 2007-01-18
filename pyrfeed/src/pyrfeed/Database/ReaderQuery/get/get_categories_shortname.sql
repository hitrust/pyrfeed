SELECT
    Categorie.shortname
FROM
    Item,
    ItemCategorie,
    Categorie
WHERE
    Item.google_id = '%(google_id)s'
    AND
    Item.idItem = ItemCategorie.idItem
    AND
    ItemCategorie.idCategorie = Categorie.idCategorie
ORDER BY
    Categorie.shortname
