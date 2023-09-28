# UniProt usage in PROTzilla
To make use of the UniProt integration in PROTzilla, tables with information on
proteins need to be added to PROTzilla via the Databases page. Afterward, they
can be used for Gene mapping if they contain a `Gene Names` or `Gene Names 
(primary)` column, or for adding UniProt data to a PROTzilla table.

Frequently used tables can be found where PROTzilla is released, at 
https://github.com/cschlaffner/PROTzilla2/releases .
By using the UniProt website at https://www.uniprot.org/uniprotkb?query= , 
tables, that contain the proteins that interest you with the columns that you
need, can be downloaded.


### How to query UniProt

In the sidebar on the left, you can choose if you want all proteins, or just
the reviewed ones, as well as select proteins by species or other 
characteristics. If you are interested in characteristics that are not shown or
want to choose a different organism, you can use the "Advanced" button in the
search bar at the top. With the advanced search, you can build complex 
conditions for what proteins should be contained in the result out of pairs of
field and value, such as "Taxonomy: Homo sapiens AND Reviewed: Yes". More
information can be found at https://www.uniprot.org/help/filter_options
The number of results is shown above the table that displays the first few
results. The columns that are visible can be changed with the 
"Customize columns" button above the table. There is a vast selection of 
columns available.


### Downloading from UniProt

When you have selected the proteins that you want to download to be added to
PROTzilla, you can click the "Download" button above the table. In the "Format"
selector, you need to choose "TSV". If you select "Compressed: Yes", you will
need to decompress the file before adding it to PROTzilla.

In the "Customize columns" section, you need to choose the columns that you
want to have available in PROTzilla. When you click the "Download" button at
the bottom, a browser download will start. The download could take several 
minutes if you have selected more than 100,000 proteins or many columns. If you
have selected more than 10,000,000 proteins, the file will be generated and you
can download it later.


### Adding to PROTzilla

As a last step, the downloaded file needs to be added to PROTzilla. This is
done via the databases page, which can be reached by clicking on the "Manage 
Databases" button on the main page. Then, you have to input a name and select 
the file for upload. After the "Add new database" button is clicked, the table
is available for adding info and mapping genes, and is listed at the bottom of
the tables page.
