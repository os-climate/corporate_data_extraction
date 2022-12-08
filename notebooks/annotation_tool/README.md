# Annotation Widget Notebook!

This **Notebook** will help you annotate the output of the ML Solution . The basic steps will be described below.


## Files

The csv file you want to annotate should be placed in the **/output** folder. It should contain *kpi*, *paragraph* and *answer* columns.
Specify the file name in the notebook
`file_name = "test_predictions_kpi.csv"`

## Run all cells

Once the file name is set, run all the cells. 
![run_all](/images/01_run_all.png)
If everything ran correctly, your view should be the following:
![run_result](/images/02_run_view.png)
## Annotate

When you annotate you have the option to declare the answer as correct, incorrect, or partial when the paragraph only is correct.
When only the paragraph is correct you have the option to insert the correct answer inside a textbox and click enter once it is done
![correct paragraph](/images/03_correct_paragraph.png)
## Skip Questions

Questions can be skiped if wished to if they are already answered to.

## Save results

The annotation can be paused and saved by clicking the Save button, or it will be automatically saved when reaching the final line of the excel file.
![annotation_finished](/images/04_annotation_finished.png)
