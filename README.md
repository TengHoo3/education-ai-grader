# education-ai-grader
basically this is the high level - goal is to automatically grade student answers from a test. We have access to the following:
 1.⁠ ⁠student answer
 2.⁠ ⁠⁠model answer
 3.⁠ ⁠⁠question paper
What we wanna do is grade the student answer and:
 1.⁠ ⁠give a final marking
 2.⁠ ⁠⁠explain where they went wrong for each question

Solution:
 1.⁠ ⁠use OCR to grab text from pdf/images —> image to text
 2.⁠ ⁠⁠from the text, we need to do some preprocessing before passing to LLM (ideally this is what we want, the more cleaning we can do for the LLM the better)
 3.⁠ ⁠⁠pass to LLM in prompt format (prompt engineering comes in here)
 4.⁠ ⁠⁠get final output
	a. We want to get a final table output of the overall marks so it is easier for the user to see and compare the marks
	b. explanation for each question on where the student went wrong