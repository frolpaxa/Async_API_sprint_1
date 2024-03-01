__GENERAL = """
    SELECT
        FW.ID,
        FW.TITLE,
        FW.DESCRIPTION,
        FW.RATING,
        FW.TYPE,
        FW.UPDATED_AT,
        COALESCE (
            JSON_AGG(
                DISTINCT JSONB_BUILD_OBJECT(
                    'PERSON_ROLE', PFW.ROLE,
                    'PERSON_ID', P.ID,
                    'PERSON_NAME', P.FULL_NAME
                )
            ) FILTER (WHERE P.ID IS NOT NULL),
            '[]'
        ) AS PERSONS,
        ARRAY_AGG(DISTINCT G.NAME) AS GENRES
"""

MOVIES = (
    __GENERAL
    + """
    FROM CONTENT.FILM_WORK FW
    LEFT JOIN CONTENT.PERSON_FILM_WORK PFW ON PFW.FILM_WORK_ID = FW.ID
    LEFT JOIN CONTENT.PERSON P ON P.ID = PFW.PERSON_ID
    LEFT JOIN CONTENT.GENRE_FILM_WORK GFW ON GFW.FILM_WORK_ID = FW.ID
    LEFT JOIN CONTENT.GENRE G ON G.ID = GFW.GENRE_ID
    WHERE FW.UPDATED_AT > %s
    GROUP BY FW.ID
    ORDER BY MAX(FW.UPDATED_AT), FW.ID;
"""
)

MOVIE_PERSONS = (
    __GENERAL
    + """
    FROM CONTENT.PERSON P
    LEFT JOIN CONTENT.PERSON_FILM_WORK PFW ON PFW.PERSON_ID = P.ID
    LEFT JOIN CONTENT.FILM_WORK FW ON FW.ID = PFW.FILM_WORK_ID
    LEFT JOIN CONTENT.GENRE_FILM_WORK GFW ON GFW.FILM_WORK_ID = FW.ID
    LEFT JOIN CONTENT.GENRE G ON G.ID = GFW.GENRE_ID
    WHERE P.UPDATED_AT > %s
    GROUP BY FW.ID
    ORDER BY MAX(P.UPDATED_AT), FW.ID;
"""
)

MOVIE_GENRES = (
    __GENERAL
    + """
    FROM CONTENT.GENRE G
    LEFT JOIN CONTENT.GENRE_FILM_WORK GFW ON GFW.GENRE_ID = G.ID
    LEFT JOIN CONTENT.FILM_WORK FW ON FW.ID = GFW.FILM_WORK_ID
    LEFT JOIN CONTENT.PERSON_FILM_WORK PFW ON PFW.FILM_WORK_ID = FW.ID
    LEFT JOIN CONTENT.PERSON P ON P.ID = PFW.PERSON_ID
    WHERE G.UPDATED_AT > %s
    GROUP BY FW.ID
    ORDER BY MAX(G.UPDATED_AT), FW.ID;
"""
)

GENRES = """
    SELECT 
        ID
        ,NAME
        ,DESCRIPTION
        ,CREATED_AT
        ,UPDATED_AT
	FROM CONTENT.GENRE
        WHERE UPDATED_AT > %s 
"""

PERSONS = """
    SELECT
        P.ID,
        P.FULL_NAME,
        P.UPDATED_AT,
        ARRAY_AGG(
            DISTINCT JSONB_BUILD_OBJECT('ID', PFW.FILM_WORK_ID, 'ROLE', PFW.ROLE)
        ) FILTER (WHERE P.ID = PFW.PERSON_ID) AS FILMS
    FROM CONTENT.PERSON P
    LEFT JOIN CONTENT.PERSON_FILM_WORK PFW ON P.ID = PFW.PERSON_ID
        WHERE P.UPDATED_AT > %s
    GROUP BY P.ID
    ORDER BY P.UPDATED_AT
"""
