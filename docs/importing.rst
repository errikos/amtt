Importing the generated files
-----------------------------

Normally, the generated files are ready to import to the target software. Follow the instructions that are outlined below for each target.

Isograph Availability Workbench
"""""""""""""""""""""""""""""""

The files generated for Isograph are in XML format. To import them you will need to create a new, empty project.

The steps are outlined below:

1. Choose **File** -> **Import**.

2. In the **Database** tab, select **Type**: XML File.

3. In **File**, click browse and select the XML file generated by the translator.

4. In the **Schema** tab you can see the generated schema (the tables and the columns of each table).

5. Go to the **Table Matches** tab and click "**Auto match**". The external tables should match automatically.

6. Go to the **Column Matches** tab. For each entry in the "**Table match**" drop-down menu, select "**Auto match**". The external columns should match automatically.

7. Save the import template if you wish, by clicking **Save**.

8. Finally, click **Import**. The model should get imported.