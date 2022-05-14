# CEV viviendas database (web scraper)
This database contains the data about rated homes under the program ["Calificación energética de viviendas CEV"](https://www.calificacionenergetica.cl/).

### Extract
* Data dowloaded from the website address: 'http://calificacionenergeticaweb.minvu.cl/Publico/BusquedaVivienda.aspx' 

* Scrapping process is made by:
    * Region
        * Comunas per region
            * Precalificacion
                * Page by page (it can be more than one)
            * Calificacion
                * Page by page (it can be more than one)
* At every single page:
    * request.post method by providing a form_data dictionary with:
        * eventtarget: str
        * eventargument: str
        * region: str
        * comuna: str
        * certification: str (Precalification: '1' / Calificacion: '2' )    
    * Response as html code to be scrapped
    * Scrapped data converted into a pandas dataframe with 5 columns:
        * Identificación Vivienda: str	
        * Tipología: str
        * Comuna: str
        * Proyecto: str
        * CE: str
        * CEE: str
    * Scrapped data save in for of csv files:
        * 1 folder per region
        * 1 file per region/comuna/certification (i.e. '1_5_1.csv')