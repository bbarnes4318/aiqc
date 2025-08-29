import re
import pandas as pd

# Define the call summaries as a long string
call_summaries = """
PS C:\Users\Jimbo\Documents\FE Python Transcription App> .\venv\Scripts\Activate
(venv) PS C:\Users\Jimbo\Documents\FE Python Transcription App> python feall.py
Processing: https://media.ringba.com/recording-public?v=v1&k=EdXy2dxqxJAMYS3bHYsvoRChGY%2f%2f9rwsQxxQIlaW4qy2s8ss3IYAEXmpgrAQZ1Be6G4rmPsVaG5erkdBi3ZvSRez0O%2fPC1%2fhhV0ylY7e92dHTPr3Jo2wG5gcm8wGpZ6pgj2UA%2fPrNk1kvdNgDLqmhJ%2fRBESd%2btcEic2zmAzf8MlBXFTycyxO9tk1vUmlqc%2fx0nj06RkioZOVwZdQnKHXk0Epzk1DPCbxp1smgAuOcDMturwDneRGYTZL6fmFFktk1CQDuYiCsFtXB39igo7WQpzJeSI%3d
Analysis Result:
 ### Analysis:

#### 1. **Billable Call Determination:**
The call does qualify as a billable call based on the provided criteria:
- The customer does not mention residing in a nursing home.
- The customer does not mention being diagnosed with COPD.
- The customer tried to provide payment details but had issues confirming as the agent tried multiple banks, showing intent to have a payment method.
- There is no mention of the customer requiring a power of attorney for financial decisions.
- The customer is aware that the call is about final expense or life insurance.
- There is no indication that the customer is on the call solely to waste the agent's time or as a prank.

Thus, this is a **Billable Call**.

#### 2. **Final Expense Application Determination:**
No application for final expense insurance was submitted because the customer did not successfully provide:
- Checking account number and routing number.
- Savings account number and routing number.
- Debit card number.
- Credit card number.

#### 3. **Quote Provided Determination:**
Since an application was not submitted, we need to describe the last quote given to the customer and the reason for not purchasing the policy:
   - a. Monthly Premium: $30.14
   - b. Insurance Carrier: CVS Health
   - c. Coverage Amount: $2,000
   - d. Policy Type: **Guaranteed Issue** (Given her age and the context of the discussion, this would fit the best.)
   - e. Reason for not purchasing the policy: The call was disconnected before bank account information could be verified and submitted.
   - f. Follow-up set: **No**

#### 4. **Abrupt Ending to the Phone Call Determination:**
   - a. Did the call end abruptly? **Yes**
               - 1. Were medical questions already answered? **Yes**
               - 2. Did the customer already agree to a coverage amount and monthly premium? **Yes**
               - 3. Did the customer already choose a beneficiary? **Yes**
               - 4. Did the customer already give a social security number? **Yes**
               - 5. Did the customer already provide their bank account routing and account numbers OR a credit card number? **No**
               - 6. What was the last question asked before the call ended abruptly? The agent was attempting to contact the correct bank to obtainthe routing and account numbers.

### Summary:
1. **Billable Call:** Yes
2. **Was an application submitted?** No
3. **Quote Details:**
   - Monthly Premium: $30.14
   - Insurance Carrier: CVS Health
   - Coverage Amount: $2,000
   - Policy Type: Guaranteed Issue
   - Reason for not purchasing: The call was disconnected before the bank account information could be verified and submitted.
   - Follow-up set: No
4. **Did the call end abruptly?** Yes
   - Medical questions answered: Yes
   - Coverage amount and monthly premium agreed: Yes
   - Beneficiary chosen: Yes
   - Social security number given: Yes
   - Bank account routing and account numbers or credit card number provided: No
   - Last question asked: The agent was attempting to contact the correct bank to obtain the routing and account numbers.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=UVBTCcMmrDRQ50PItrdRdmtYiAcdQR%2ff3UaiQZmkrLaF3wWskdIx9Fj1NhlfC8KUY8p2SD6aRAs0dwAFR2Eq9xqwmYZY3MzETsm2oQJ%2f9TYSRmtE1CKtplYaboVDllgPYYo6HVwI%2frPa4%2fU8oVgVY1HYGqzn0l%2bdhM5QAipFz%2fwZQF8UPT9VIxl%2fGQJ%2bu6ezrSypgUIJzVCViy7CwB%2fB%2besmbdBAk6%2fa3834C036Y7M7j4oHmEM%2f5i5aJ2kEWvBchLM%2b5HsxuokrkyWJXMglsalhal8%3d
Analysis Result:
 ### Call Analysis

1. **Billable Call Determination:**
   - a. The transcript does not indicate that the customer resides in a nursing home.
   - b. There is no mention of the customer being diagnosed with COPD.
   - c. The customer has an active bank account, as indicated by their statement about possessing account and routing numbers.
   - d. There is no indication that the customer requires a power of attorney for financial decisions.
   - e. The customer clearly understands that the call is about final expense or life insurance.
   - f. There is no indication that the customer is on the call solely to waste the agent's time or as a prank.
   - **Conclusion:** The call is **Billable**.

2. **Final Expense Application Determination:**
   - The customer did **not** provide a checking account number and routing number, savings account number and routing number, debit card number, or credit card number.
   - **Conclusion:** **No application** was submitted.

3. **Quote Provided Determination (since no application was submitted):**
   - a. **Monthly Premium:** $178.68
   - b. **Insurance Carrier:** CVS Health
   - c. **Coverage Amount:** $20,000
   - d. **Policy Type:** Level
   - e. **Reason for not purchasing the policy:** The customer was unable to find their banking information to complete the application process.
   - f. **Was a follow-up set?** No, there is no indication of a follow-up being set in the transcript.

4. **Abrupt Ending to the Phone Call Determination:**
   - a. **Did the call end abruptly?** Yes
       - 1. **Were medical questions already answered?** Yes
       - 2. **Did the customer already agree to a coverage amount and monthly premium?** Yes
       - 3. **Did the customer already choose a beneficiary?** Yes
       - 4. **Did the customer already give a social security number?** Yes
       - 5. **Did the customer already provide their bank account routing and account numbers OR a credit card number?** No
       - 6. **What was the last question asked before the call ended abruptly?**
           - The last question before the call ended abruptly was: "Peggy, your account and routing number."

### Summary
- **Billable Call:** Yes
- **Application Submitted:** No
- **Quote Provided:** Yes
    - Monthly Premium: $178.68
    - Insurance Carrier: CVS Health
    - Coverage Amount: $20,000
    - Policy Type: Level
    - Reason for Not Purchasing: Customer couldn't find banking information
    - Follow-up Set: No
- **Abrupt Ending to the Phone Call:** Yes
    - Medical questions answered: Yes
    - Agreed on coverage and premium: Yes
    - Beneficiary selected: Yes
    - Social Security number provided: Yes
    - Bank account details provided: No
    - Last question before abrupt ending: Requesting account and routing numbers
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=cHu%2bRGs5FmIdRpV6Uc9PxoNQd%2fig74W%2bIREMtn%2fc%2bqpqJQtbhOLunA1SjEtGKwrl9VeStP8xjmsSeBfxWY1B7Wp9YAMBsqoynQLsLyKSunrvHO9Dzfqz9Vle1S5MVWT5dJh5VmpHxHR8O5KHRVl6vwzJs5Sr0peSFxChmAaSyjJ71E6XYaC%2fPE18m9d3JXKH5xDb68eWgFbEji6JanRDVg%2bi6sNcLbkpC5q2clScT9if8HFotACo%2fKmcj2oEZmGFL2jMgHN29oYoAf3zXaKeYUnoAbg%3d
Analysis Result:
 Based on the call transcript, here are the findings for each objective:

1. **Is the call a billable call?**
   - The call is **Billable** because none of the conditions for making it non-billable were met. The customer, Sheila Remley, does not reside in anursing home, does not have COPD, did not state she lacks an active payment method, does not require a power of attorney, is aware that the call isabout final expense insurance, and is not on the call to waste the agent's time.

2. **Was an application submitted?**
   - An application was **not** submitted during the call. Sheila did not provide any checking account, savings account, debit card, or credit cardnumbers.

3. **Quote Provided Determination:**
   - a. **Monthly Premium:** $53.24
   - b. **Insurance Carrier:** Mutual of Omaha
   - c. **Coverage Amount:** $10,000
   - d. **Policy Type:** Level (The agent aimed for first-day coverage indicating good health coverage, although Sheila has health issues which could potentially affect this).
   - e. **Reason for not purchasing the policy:** Sheila wanted to confirm how the transition would work if she canceled her current policy. She needed assurance regarding the cash value and transition process.
   - f. **Was a follow-up set?** No, a specific day and time were not mentioned for a follow-up.

4. **Abrupt Ending to the Phone Call Determination:**
   - a. **Did the call end abruptly?** Yes, the call ended abruptly.
       - 1. **Were medical questions already answered?** Yes, medical questions were answered earlier in the call.
       - 2. **Did the customer already agree to a coverage amount and monthly premium?** Yes, the customer agreed to a $10,000 coverage amount and a monthly premium of $53.24.
       - 3. **Did the customer already choose a beneficiary?** No, a beneficiary was not chosen or discussed.
       - 4. **Did the customer already give a social security number?** No, the social security number was not provided.
       - 5. **Did the customer already provide their bank account routing and account numbers OR a credit card number?** No, these details were notprovided.
       - 6. **What was the last question asked before the call ended abruptly?** The last question asked was the customer's address and whether shewas born in California or moved to California.

The call process shows that much of the necessary information was gathered, but the application submission did not go through. There were several points of confirmation left such as agreeing on the final steps and transitioning from the existing policy before the abrupt end.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=eWX9eqJ4TVSzfYpZExa8KGlaLdte0dAAul6rzfxC6SlmOoTfxfzSBpxplQSjR6h7Px9YMuVH9Ae2bGWbgSgqkG7gV9lgWoNAzIVhS0oWV6esAKdFUEgsz07Y461v7YNV02%2f5NCu4jNq9wAqHL1riCmi01yG%2fXAlnTIFClmecG5XgfhBpd4JfEzFhOW4QOz1uvvUtD%2bT05y0jiLT%2fasuFG5dGbqLrbSeRfmjv7yek9t%2b%2fk1eVSVZpIoPth4zBh96ofKqb1YZ%2bVzxOXboUu%2fYR8cg%2fcXI%3d
Analysis Result:
 ### Objectives:

**1. Is the call a billable call?**

**Billable Call Determination:**
- This call qualifies as billable. None of the following disqualifying conditions were met:
  - The customer does not reside in a nursing home.
  - The customer has not been diagnosed with COPD.
  - The customer explicitly states they have an active payment method, providing details of their bank account.
  - The customer does not require a power of attorney for financial decisions.
  - The customer is aware that the call is about final expense or life insurance.
  - The customer is not on the call solely to waste the agent's time or as a prank.

**2. Was an application submitted?**

**Final Expense Application Determination:**
- An application for final expense insurance was **not** submitted during the call. Though the customer provided their checking account number and routing number, the application couldn't be completed due to identity verification issues.

**4. Quote Provided Determination:**

Since an application was not submitted, the following quote details were provided by the agent:

   - a. **Monthly Premium:** $94.46
   - b. **Insurance Carrier:** Aetna
   - c. **Coverage Amount:** $15,000
   - d. **Policy Type:** Level (as the customer is in good health with immediate first-day coverage).
   - e. **Reason for not purchasing the policy:** The customer had issues with verifying their identity and needed to retrieve their driver's license, which was not immediately accessible. Also, the customer had to go to a dental appointment.
   - f. **Was a follow-up set?** Yes. A follow-up call was scheduled for 4:00 PM on the same day.

**5. Did the call end abruptly?**

- **Did the call end abruptly?** No, the call did not end abruptly.

### Summary:
- **Billable Call:** Yes
- **Application Submitted:** No
- **Quote Provided:**
  - Monthly Premium: $94.46
  - Insurance Carrier: Aetna
  - Coverage Amount: $15,000
  - Policy Type: Level
- **Reason for Not Purchasing:** Issues verifying identity and needing to attend a dental appointment.
- **Follow-up Scheduled:** Yes, 4:00 PM on the same day.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=jwYdKPDTVT3%2bixavCpoDPSLHQBbCAfB0k571xKhEgrUdnGpo9M2xvjnfPIAz%2b7%2fyruKe4anRj7moKUJML4HtFav08gjavhlfiMeK7fqFnU%2fhLzcLphO44T82fGNyG2fVKlisgbcYnR7xmOMHOfwas7ErDKf2Rx8Ih8OIS2BvQfTkOowx0WjBk%2bH3jX95%2fCfo4S%2bMv2pOw%2fbJEhiu%2bxAgzXB94LlKn40%2fQKbNwA%2bxJfGaKmtQQVW8hJxlnm2zDzT3LDRP3Qxf8Xw15M%2fFbCsxCV25dJI%3d
Analysis Result:
 ### Analysis

1. **Is the call a billable call?**
   - **Billable Call Determination:**
     - The customer does not reside in a nursing home.
     - The customer does not have COPD.
     - The customer did not explicitly state that they do not have an active payment method (e.g., bank account, debit card, or credit card).
     - The customer does not require a power of attorney for financial decisions.
     - The customer is aware that the call is about final expense or life insurance.
     - The customer is not on the call solely to waste the agent's time or as a prank (though they were largely non-committal and digressed a lot).

   **Conclusion:** The call is billable.

2. **Was an application submitted?**
   - **Final Expense Application Determination:**
     - No checking account number or routing number was provided.
     - No savings account number or routing number was provided.
     - No debit card number was provided.
     - No credit card number was provided.

   **Conclusion:** An application was not submitted.

3. **Quote Provided Determination:**
   - The agent did not successfully provide a complete quote with specific details such as the monthly premium, insurance carrier, coverage amount,or policy type because the customer was evasive and did not commit to proceeding.
   - **Reason for not purchasing the policy:** The customer was not prepared to make a decision and had other concerns to address.
   - **Follow-up set:** No follow-up was set.

4. **Abrupt Ending to the Phone Call Determination:**
   - **Did the call end abruptly?** No, the call did not end abruptly. The agent concluded the call after a lengthy and somewhat unfocused discussion with the customer.

### Summary of Answers:

1. **Billable Call:** Yes
2. **Application Submitted:** No
3. **Quote Provided:**
   - a. Monthly Premium: Not provided
   - b. Insurance Carrier: Not provided
   - c. Coverage Amount: Not provided
   - d. Policy Type: Not provided
   - e. Reason for not purchasing the policy: The customer was not ready to make a decision and had other concerns.
   - f. Follow-up set: No
4. **Call Ending Abruptly:** No
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=wnQEzesCdbKgWR3qM8DuSxdVpNkh99PVawz%2fDd3LsG%2bWhExlixdyhtptQRvOv3xsT%2fFmsqeQRPEUinB17i%2fJ1Nq1gka87ry48Z9n764UUaJbnFwEj96J9lZsX8Jn%2bnDm30mL6HjVXNEeZo3GTk%2bMt%2fVkMT7Dytk%2fhBqaRDU0JSO%2bjvgkDfF6skBG%2ffqUUlt7%2fgvYacTU%2b5RneQsghSGuvqk0O%2bZc8JY559kLNaaqYea7PlkjVkjecnewxtWyJ89beN%2ffWSOYLYoZ7v9YXjT%2fyju91z0%3d
Analysis Result:
 ### Objectives:

#### 1. Is the call a billable call?

**Billable Call Determination:** Yes, the call is billable. None of the following conditions apply:
   - The customer does not reside in a nursing home.
   - The customer does not have COPD.
   - The customer did not explicitly state they do not have an active payment method.
   - The customer did not require a power of attorney for financial decisions.
   - The customer was aware the call is about final expense/life insurance.
   - The customer was not on the call to waste the agent's time or as a prank.

#### 2. Was an application submitted?

**Final Expense Application Determination:** No, an application was not submitted.

#### 3. If an application was submitted, provide:

N/A (An application was not submitted).

#### 4. **Quote Provided Determination:**

Since an application was not submitted, details of the quote offered:

   - a. Monthly Premium: $42.22
   - b. Insurance Carrier: Aetna
   - c. Coverage Amount: $3,000
   - d. Policy Type: Level (based on first-day coverage)
   - e. Reason for not purchasing the policy: The customer needed to locate his wallet for his license number, and the call could not be completed as the agent suggested calling back.
   - f. Was a follow-up set?: Yes, the agent suggested calling back on the customer's cell phone. No specific day and time were mentioned, but it was implied to be immediate.

#### 5. **Abrupt Ending to the Phone Call Determination**

**a. Did the call end abruptly?**
   - Yes.

        **1. Were medical questions already answered?**
           - Yes, the customer answered questions about high blood pressure.

        **2. Did the customer already agree to a coverage amount and monthly premium?**
           - Yes, the customer agreed to $3,000 coverage for $42.22 per month.

        **3. Did the customer already choose a beneficiary?**
           - No, the customer did not choose a beneficiary.

        **4. Did the customer already give a social security number?**
           - No, the customer did not provide their social security number.

        **5. Did the customer already provide their bank account routing and account numbers OR a credit card number?**
           - No, the customer did not provide their bank account or credit card number.

        **6. What was the last question asked before the call ended abruptly?**
           - The last question was for the customer's cell phone number to send a six-digit code for the e-signature process, followed by a requestfor the customer's email address for the application.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=JALztB%2bC0kVPCKUYAtq2UzyOLFcMEkDu%2fvQU1728VFjLOxRdZXz09x4YuzOCCp4uOoGuxMT1RVl30jIzBj2wp%2f2q6wPDdR4hY0ypzZUegk%2frju1WBQ8H4n9JUbe975JLayEjrTphZDh2ofXkynf3ph%2frSQvu1hwweQx6vCTgsQyA%2boX0wJrOOd7pQU5dzDsp%2bWJYYvmKd4qXQhiLRx7u1gkIpZ8UuozuoitBcddmkTYGrkTK7uJE442YIwQZA8ApefmN2HcmOWrOLKfNMrbXSFttekQ%3d
Analysis Result:
 ### Objectives:

**1. Is the call a billable call?**

**Answer:** No, the call is not billable. The customer, Betty Hale, explicitly states she does not currently have an active bank account due to having been hacked and needing to reopen her account. This qualifies under condition (c): "The customer explicitly states they do NOT have an active payment method."

**2. Was an application submitted?**

**Answer:** No, an application was not submitted. Betty Hale did not provide any checking account number, routing number, debit card number, or credit card number during the call.

**3. If an application was submitted, provide:**

**Answer:** Not applicable, as no application was submitted.

**4. Quote Provided Determination:**

   - a. **Monthly Premium:** $72.19 per month
   - b. **Insurance Carrier:** Not specified in the transcript.
   - c. **Coverage Amount:** $10,000
   - d. **Policy Type:** Level
   - e. **Reason for not purchasing the policy:** The customer needs to resolve her banking issues first. Her bank account was closed due to being hacked, and she is waiting for it to be reopened.
   - f. **Was a follow-up set?:** Yes. The agent set a follow-up call for tomorrow morning.

**5. Abrupt Ending to the Phone Call Determination:**

**Answer:** No, the call did not end abruptly. The agent and the customer agreed to a follow-up call for the next day to finalize the application, so the conversation ended on a mutually agreed note.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=iWJO3boC%2fL5rccUQbRXBmM90vi4xIY9vg44ppFfscj%2bH2ie0SColP%2biPF64KxkMF04vvGlKS1PNkWwsY1RW%2fQ7cwkT6NHQIHO3tvo5Q0q7%2fAVfGE3jQXt6ja8nS5qIgmqdNo6aOyhU0BEttym8NXimjxLfmCKap9Trx%2bpis9mweptdRJuO7JM1yDuk3%2b%2f%2bTFAu4vIlctqIwnWe0KxzNrtHFEd80Gw05DTF0xnZ9PzaT6FrS1yZWRtgYpkpdhtYcrGT0PVISkLjot0MVLMIFXX1kHCdY%3d
Analysis Result:
 ### Call Analysis

1. **Is the call a billable call?**
   - **Billable Call Determination:** No.
     - **Reason:** The customer, Terry, explicitly stated that he has no money currently and does not have an active Social Security income yet (mentioned around "Oh, I don't know when I'm gonna get it. I don't know what I'm gonna get it. I don't know when I'm gonna get it. I've been on it almost three years now trying to get it. Haven't got any yet."). Therefore, he does not currently have an active payment method.

2. **Was an application submitted?**
   - **Final Expense Application Determination:** No.
     - **Reason:** The customer did provide an account number but did not provide a routing number or any other required banking information. The application was not fully completed.

3. **If an application was submitted, provide:**
   - **N/A** (No application was submitted).

4. **Quote Provided Determination:**
   - **Quote Details:**
     - a. **Monthly Premium:** $35.95
     - b. **Insurance Carrier:** Mutual of Omaha
     - c. **Coverage Amount:** $10,000
     - d. **Policy Type:** Level
     - e. **Reason for not purchasing the policy:** Customer does not have an active payment method and is waiting for Social Security disability payments.
     - f. **Was a follow-up set?:** No specific follow-up time was agreed upon. The agent suggested to start the policy at the end of September, hoping the customer’s Social Security would come through by then.

5. **Abrupt Ending to the Phone Call Determination:**
   - **Did the call end abruptly?** Yes.
     - 1. **Were medical questions already answered?** Yes.
     - 2. **Did the customer already agree to a coverage amount and monthly premium?** Yes.
     - 3. **Did the customer already choose a beneficiary?** Yes.
     - 4. **Did the customer already give a social security number?** Yes.
     - 5. **Did the customer already provide their bank account routing and account numbers OR a credit card number?**
       - **Bank account number:** Yes (143-200-8066).
       - **Routing number:** No.
     - 6. **What was the last question asked before the call ended abruptly?**
       - The agent was confirming the customer's first name and the spelling of his surname, "Maria. M a r I o t. Correct. Marr double R. Yes, sir.Okay."

### Summary:
- **Billable Call:** No
- **Application Submitted:** No
- **Quote Provided:**
  - Monthly Premium: $35.95
  - Insurance Carrier: Mutual of Omaha
  - Coverage Amount: $10,000
  - Policy Type: Level
  - Reason for not purchasing the policy: No active payment method.
  - Follow-up set: No
- **Abrupt Call Ending:**
  - Yes, the call ended abruptly as the agent was confirming the customer's details.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=isZB%2fzVp6oT%2fytiLNOXid9h%2fGRN5xera%2fL9z4wGXdHX%2bFLBmN0WMLZenSCwRJQZqGuCBYuJeglYzRRLjltMDUb1I2V1vyMKlab12gEu953KfO19HXutkY4fjCJe6RNSMDbeq%2bW6z7T5OSsSOO6hgig5WBQZ9DJkvtoQR64E1Fb1orGLC50XZR9jiGhKY2JpDHTRYniLTwtmAjsoikrqP22btR9%2fREbu%2bWQF20fELxiz6u09Bo%2bhjiexJ4jsahaYk1A08WhRBm7nieyXsyrgbRJYy22A%3d
Analysis Result:
 ### Objectives:

#### 1. Is the call a billable call?
**Billable Call Determination:**
- The customer explicitly states that they do NOT have an active payment method (e.g., bank account, debit card, or credit card).
- The customer doesn't provide any valid payment information during the call, making it non-billable.

Therefore, the call is **not billable** because the customer explicitly stated they don't have an active payment method.

#### 2. Was an application submitted?
**Final Expense Application Determination:**
- No application was submitted. The customer did not provide checking account number, routing number, debit card number, or credit card number.

#### 3. Quote Provided Determination
Since an application was not submitted, the following are the details of the quote offered by the agent:

- **a. Monthly Premium:** $39.68
- **b. Insurance Carrier:** Aetna CBS
- **c. Coverage Amount:** $5,000
- **d. Policy Type:** Level (Implied as the customer is in good health)
- **e. Reason for not purchasing the policy:** The customer needs to locate bank and routing information and was unsure if they wanted to proceed.
- **f. Was a follow-up set?:** Yes. The agent asked if there was a better time to call for the bank and routing information but no specific day andtime were set.

#### 4. Abrupt Ending to the Phone Call Determination
**Abrupt Ending Determination:**
- **a. Did the call end abruptly?** Yes

If So:
   - **1. Were medical questions already answered?** Yes
   - **2. Did the customer already agree to a coverage amount and monthly premium?** Yes
   - **3. Did the customer already choose a beneficiary?** Yes
   - **4. Did the customer already give a social security number?** Yes
   - **5. Did the customer already provide their bank account routing and account numbers OR a credit card number?** No
   - **6. What was the last question asked before the call ended abruptly?** The last part of the conversation involved the customer looking for bank and routing information but not providing it: "Take your time. Hello, Ms. Joanne. Hello, Ms. Joan. Hi, Ms. Joanne. Ms. Joanne? Yeah. Hi, Miss Joanne. Miss Joanne. Hi, Miss Joanne."
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=c%2bG6SvAdj%2bvp4uiVD2IrG9sszBnoi%2fcgVJ6g6hIBQOF4lvJCfh549Ka5eZT0FRFYAQmed2Ga5VdDzxR3Hnbm4wtvLhwqjdHsLCZNLreIMEK2qS1WEFf2VznKNSiI625QzGHC6geosRfFKGL8bz6pdv4NDDvcpGFcYCkKTiim4B7dr1mAYQI%2bt4nmLoS14zT4Y8Hh4JTwW3aRBSYmOvlGmpPLSRLCNWLfO0elgObWUhNvfn8OObj4wanalGUxX%2b592TjT%2f3k8ox3rxIeEzDgAJfyfvHk%3d
Analysis Result:
 ### Objectives:

1. **Is the call a billable call?**
   - Yes, the call is billable. The customer, Christina, did not meet any of the conditions that would make the call non-billable:
     - She does not reside in a nursing home.
     - She has not been diagnosed with COPD.
     - Although she initially did not provide her bank details, she eventually agreed to the terms of a different billing method.
     - She does not require a power of attorney for financial decisions.
     - She is aware the call is about final expense or life insurance.
     - She is not on the call solely to waste the agent's time or as a prank.

2. **Was an application submitted?**
   - No, an application was not submitted. Christina did not provide any checking account number, routing number, debit card number, or credit cardnumber.

3. **Quote Provided Determination:** Since an application was not submitted, the quote details are as follows:
   - a. Monthly Premium: $47.60
   - b. Insurance Carrier: Aetna (CVS Health)
   - c. Coverage Amount: $15,000
   - d. Policy Type: Level (as no health issues were discussed that would indicate otherwise)
   - e. Reason for not purchasing the policy: The application was declined by underwriting.
   - f. Was a follow-up set? No specific follow-up was set.

4. **Abrupt Ending to the Phone Call Determination**
   - a. Did the call end abruptly? No, the call did not end abruptly.
        - 1. Were medical questions already answered? Yes, medical questions were answered.
        - 2. Did the customer already agree to a coverage amount and monthly premium? Yes, Christina agreed to $15,000 coverage for $47.60 per month.
        - 3. Did the customer already choose a beneficiary? Yes, the beneficiary chosen was her son, Deandre Baylock.
        - 4. Did the customer already give a social security number? Yes, Christina provided her Social Security number.
        - 5. Did the customer already provide their bank account routing and account numbers OR a credit card number? No, Christina did not providea bank account or credit card number.
        - 6. The call did not end abruptly; it concluded after the agent informed Christina about the application denial. The last question before the call ended was not applicable as the call ended properly.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=2y0AlOwWHURsBxvD%2bcjdX1qhwGow%2bXFZPR1X4cYY20EPlNa6giUxE7BzdiqVjTOl3o0%2fidMCujeGeNuHqcANzP1xZHKSQyJBv4wooYhsRwIzv2vidpNny1a5o0CfAxSLNyqlh4oqlJmtFuFLzeB9gm4YyUREghkeE0MrMXL2Rvy6wZbY14lxw2ErOSkUHTt6lf8OLUSlIJy37lLM8%2buNmFEx40mSYZ7z5M2ruzLM%2fod%2b3582NFCYkacCGMHwoJH6FUm37c4bdLK5wgFI70C1nZlZfQY%3d
Analysis Result:
 ### Analysis of the Call Transcript:

1. **Billable Call Determination**:
   - The call is considered **Billable** because none of the following conditions apply:
     - The customer does not reside in a nursing home.
     - The customer has not been diagnosed with COPD.
     - The customer did not explicitly state they do NOT have an active payment method (e.g., bank account, debit card, or credit card).
     - The customer does not require a power of attorney for financial decisions.
     - The customer was aware that the call is about final expense or life insurance.
     - The customer was not on the call solely to waste the agent's time or as a prank.

2. **Final Expense Application Determination**:
   - No, an application for final expense insurance was **not** submitted during the call because the customer did not provide a checking account number, savings account number, debit card number, or credit card number.

3. **Quote Provided Determination**:
   - Since an application was not submitted, here are the details of the quote offered by the agent:
     - **Monthly Premium**: $38.06
     - **Insurance Carrier**: CV's Health
     - **Coverage Amount**: $10,000
     - **Policy Type**: Level (as it includes first-day coverage)
     - **Reason for not purchasing the policy**: The customer did not have her bank account number or routing number handy.
     - **Was a follow-up set?**: No specific follow-up date and time were set; the customer was advised to call back when the information is available.

4. **Abrupt Ending to the Phone Call Determination**:
   - **Yes, the call ended abruptly** around the time the prospect was moving into the application for the policy.
     - 1. **Medical questions already answered?**: Yes
     - 2. **Customer agreed to a coverage amount and monthly premium?**: Yes
     - 3. **Customer chose a beneficiary?**: Yes
     - 4. **Customer gave a Social Security number?**: Yes, but there were issues with it initially.
     - 5. **Customer provided bank account routing and account numbers or credit card number?**: No
     - 6. **Last question asked before the call ended abruptly**: "Okay, and what is the name of your bank?"

In conclusion, the call is billable, no application was submitted, the quote details were provided, and the call ended abruptly during the application process.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=rKVy%2fKkgIR8yhgm955ZvOY9MrclJfYa1l33p8LogokQ3dkAOZ6dvyTVDPzXD6HMvcHhLmfgcYJyxxYLdpXB2XMZPd2IIjsenmfNctqSP5SsXRoQTmMlJ9YCGOJbpLC45BD3T7oQl6vDNdp2KoJ45rUAnLDAY35u4cA9o%2b1GguWJcbq5C%2b9DQAvjFbhGPlQanuQf3KUZZ%2fm4PDAjCQwnip5bVohfAJqSYlSaprxVFxNZQmyBpaI6jhBnrqVHgxTvFS1CVACeMaW1%2bNVaX%2f9sSGGCf41c%3d
Analysis Result:
 ### Objectives:

Based on the call transcript, you are tasked with determining the following:

1. **Is the call a billable call?**

   **Answer:** Yes, the call is a billable call. None of the conditions that make a call non-billable apply to this call:
   - The customer does not reside in a nursing home.
   - The customer has not been diagnosed with COPD.
   - The customer did not explicitly state they do not have an active payment method.
   - The customer does not require a power of attorney for financial decisions.
   - The customer is aware that the call is about final expense or life insurance.
   - The customer is not on the call solely to waste the agent’s time or as a prank.

2. **Was an application submitted?**

   **Answer:** No, an application was not submitted because the customer did not provide their checking account number and routing number, savings account number and routing number, debit card number, or credit card number.

3. **If an application was submitted, provide:**
   - **N/A** (No application was submitted.)

4. **Quote Provided Determination:**

   Since an application was not submitted, here are the details of the quote offered by the agent:

   - a. **Monthly Premium:** $58.45
   - b. **Insurance Carrier:** Not specified in the transcript.
   - c. **Coverage Amount:** $8,000
   - d. **Policy Type:** Level (customer in good health with 'first-day coverage').
   - e. **Reason for not purchasing the policy:** The customer could not find her checking account information.
   - f. **Was a follow-up set?** Yes. The agent arranged to follow up the next day to finish the application process.

5. **Abrupt Ending to the Phone Call Determination**

   - a. **Did the call end abruptly?** No, the call did not end abruptly. It concluded with the agent setting up a follow-up call for the next day.

Therefore, all required information is addressed, establishing the call as billable, noting that no application was submitted, providing the details of the quote, and confirming that the call did not end abruptly.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=1%2bu2N80PgBkVp47BB3WI4jerUD8I0VjsYK989RF3Q5fHuqG7S7kwDrW3Ak8yeV4S8GKdar2gTbaoOmVhawe5jOAFhLDoUgKugv3NWSByvCf1wOiH%2ba7HLgCIuNkXHVxgCo64CUOrSny1Tgz3KqJE0hES3KKMavdgIE977j88E4UoLIlNIHw1BwlQWF2SS6Yny8VvP5P9ENfp%2fTGUk%2feLRvMx8Y2CnVzNxwV%2bQW4ZQZttkscNLxc4UpgG7hzdAahVcsqrVa%2fQmYF0C6bQPQZOT%2fa4YRU%3d
Analysis Result:
 ### Analysis of Call Transcript

1. **Billable Call Determination:**
   - The call is **Billable** since none of the conditions that would make it non-billable are met.
   - The customer does not reside in a nursing home.
   - The customer has not been diagnosed with COPD.
   - The customer did not explicitly state they do not have an active payment method; they suggested they have the information but need to retrieveit.
   - The customer does not require a power of attorney for financial decisions.
   - The customer is aware the call is about life insurance.
   - The customer is not on the call to waste the agent’s time or as a prank.

2. **Final Expense Application Determination:**
   - No application was submitted during the call because the customer did not provide a checking account number, routing number, debit card number, or credit card number.

3. **Quote Provided Determination:**
   - a. **Monthly Premium:** $75.60
   - b. **Insurance Carrier:** Not specified.
   - c. **Coverage Amount:** $15,000
   - d. **Policy Type:** Level (since it includes same-day coverage with no waiting period)
   - e. **Reason for not purchasing the policy:** The customer did not have the bank account routing and account numbers readily available.
   - f. **Was a follow-up set?** No follow-up time and date were specified in the transcript.

4. **Abrupt Ending to the Phone Call Determination:**
   - a. Did the call end abruptly? **Yes**
     - 1. Were medical questions already answered? **Yes** (High blood pressure mentioned)
     - 2. Did the customer already agree to a coverage amount and monthly premium? **Yes**
     - 3. Did the customer already choose a beneficiary? **Yes**
     - 4. Did the customer already give a social security number? **Yes**
     - 5. Did the customer already provide their bank account routing and account numbers OR a credit card number? **No**
     - 6. What was the last question asked before the call ended abruptly?
       - The last question asked was likely concerning the completion and submission of the application, as the agent was working through the application details and preparing to conclude the conversation.

### Summary
- The call is **Billable**.
- No application was submitted due to missing payment information.
- A quote was provided, covering important details such as premium and coverage amount.
- The call ended abruptly without fully completing the application process.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=P%2bTkkimgxCOqBnPoG%2b7lH7ByyZws4igOF3fScvGVTnFMRUoZhdHaH25NjN0BqbbB%2bFS3lbUmJoDgOkbq879Shk37QiEtUwFcg51qoV1yNrudNFxLUrUs44hYJzxvOvRik5KdSv4XrXSE98w1APG0luByWILMQz9mPu%2f%2fD%2bUQ%2bwIYKNAhacrT1ZCrYK5Ea9UYZYjuVbjjoeCUDWhcXns4b5fdpQzZJ7yaPCHaZQ%2bTzxEGpCvJqbSsqFJvWN6fxNijjbURzZg9vJstYX7q0bbPaor3X4Q%3d
Analysis Result:
 ### 1. Billable Call Determination:
**Billable**

- The customer does not reside in a nursing home.
- The customer has not been diagnosed with COPD.
- The customer does not explicitly state they do NOT have an active payment method (though he mentions he will get his disability check on the third of the month).
- The customer does not require a power of attorney for financial decisions.
- The customer is aware the call is about final expense or life insurance.
- The customer is not on the call solely to waste the agent's time or as a prank.

### 2. Final Expense Application Determination:
**Application Not Submitted**

- The customer did not provide a checking account number and routing number.
- The customer did not provide a savings account number and routing number.
- The customer did not provide a debit card number.
- The customer did not provide a credit card number.

### Quote Provided Determination:
- **Monthly Premium:** $49.83.
- **Insurance Carrier:** Aetna.
- **Coverage Amount:** $15,000.
- **Policy Type:** Level (first-day coverage).
- **Reason for not purchasing the policy:** The customer did not have the immediate funds and needed the payment to be set for the third of the month.
- **Was a follow-up set?:** No explicit follow-up date or time was set during the call.

### 3. Abrupt Ending to the Phone Call Determination:
**Yes, the call ended abruptly.**

- **Were medical questions already answered?:** Yes.
- **Did the customer already agree to a coverage amount and monthly premium?:** Yes.
- **Did the customer already choose a beneficiary?:** Yes, his nephew, Guadalupe Charles Flores III.
- **Did the customer already give a social security number?:** Yes.
- **Did the customer already provide their bank account routing and account numbers OR a credit card number?:** No.
- **What was the last question asked before the call ended abruptly?:** The agent asked for the bank routing and account number.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=KyPR3EYKiBUQTjD6sYk5KcQMtqqpz2jV%2b6tiYGFz3FWtRJ058yFyFb8M%2fRKIyivMHUH2fj2NtSa%2fpbf8E6RMK3mhPxEQ5A3904hjwnR%2f3eljCABFJY71ek3o%2fXGWufUa%2fZpj2R7gH9waGrrjNTJRaqmIBTkXrX7zpxn%2fXSKqiCBUls%2fpFW8b5kSn0aGVv6Hm0qjr7%2fqudv%2fuKfbeCuEXJ88yjJp41ROk9Tn2dpzaxqtb4HTYAVCtzC2AbXtCbuljAumxUyPbgLBRD%2bEnDDNBHD8j3Kc%3d
Analysis Result:
 ### Objectives:

#### 1. Is the call a billable call?

**Billable Call Determination:** Yes, the call is billable. None of the conditions to render the call non-billable were met:
- The customer, Maggie Duckworth, does not reside in a nursing home.
- She has not been diagnosed with COPD.
- She did not state that she has no active payment methods.
- There's no indication that she requires a power of attorney for financial decisions.
- She was aware that the call was about final expense or life insurance.
- The purpose of her call was not to waste the agent's time or as a prank.

#### 2. Was an application submitted?
**Final Expense Application Determination:** No, an application for final expense insurance was not submitted.

#### 3. Since an application was not submitted:
**Quote Provided Determination:**
- a. Monthly Premium: $76.
- b. Insurance Carrier: Not specified in the transcript.
- c. Coverage Amount: $10,000.
- d. Policy Type: Guaranteed Issue based on the conversation indicating no medical exam or health conditions.
- e. Reason for not purchasing the policy: Maggie did not have her bank routing number and account number available and needed to call her bank to get this information.
- f. Was a follow-up set? Yes, the agent set a follow-up for tomorrow around noon.

#### 4. Abrupt Ending to the Phone Call Determination
- a. **Did the call end abruptly?** No, the call did not end abruptly. It ended after establishing a follow-up arrangement.

By analyzing the call transcript against the given objectives, we have obtained a thorough understanding of the call process and its status.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=pWsuxdOHfCHXHr07GOyd1mD8hhlcy89LWVwO0EnDh6eff1MET0ZPaeBdJK8GYPqMA8z8oa3H7C6OM7no3pTcAXl2YBMsXLE4fo%2f58ZlpE9GjBdb3u2ldreRXfDWeUut7R0OFWz2l0JeEDDKN9fqqFESHbVYvDg9%2f5r3dfE9vuV16Oe1d0YgNCc39MH0gGOxN2XEIPgC4EvuegIecu00Z3A1LOQkN0FR75WxgYQeFy8srkQdeZmU1af3cbLOBLFNJUJYyUInZL6lkriSO%2bxL0NQI2RoE%3d
Analysis Result:
 ### Objectives:

1. **Is the call a billable call?**
   - **Billable Call Determination:** Yes, the call is billable as none of the disqualifying conditions (a-f) apply. The customer does not reside in a nursing home, has not been diagnosed with COPD, does not state that they lack an active payment method, does not require a power of attorney, isaware the call is about life insurance, and is not on the call solely to waste the agent's time or as a prank.

2. **Was an application submitted?**
   - **Final Expense Application Determination:** No, an application for final expense insurance was not submitted during the call.

3. **If an application was submitted, provide:**
   - Not applicable as no application was submitted.

4. **Quote Provided Determination:** Since an application was not submitted, the details of the quote offered by the agent are as follows:
   - a. **Monthly Premium:** $128.29
   - b. **Insurance Carrier:** Mutual of Omaha
   - c. **Coverage Amount:** $25,000
   - d. **Policy Type:** Level (implied as the agent mentioned day-one coverage and no waiting period)
   - e. **Reason for not purchasing the policy:** The customer wanted to receive the agent's business information and verify it before proceeding.
   - f. **Was a follow-up set?:** Yes. The customer requested the agent send information via mail to their home address for further verification. No exact day or time for a follow-up call was specified, but the agent agreed to send the information and wait for the customer's return call.

5. **Abrupt Ending to the Phone Call Determination:**
   - a. **Did the call end abruptly?** No, the call did not end abruptly.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=n6ixYb3bAbZaVyk9v0qk%2bZiZxDol8B87tqFZeGTpYOzYPzpBsHgymKQL73KTFFG1hfLIvIfFLfALCkp%2b4JSU0cVoTKnwB4K2NnDzRr31BCquqUzzv3xhUsDDcwpisJoN3eq3uAVN2VZhRCzCf0JFD9a0a9EeSKPhyfUOwXGlKJm7wYjh68uFnW%2fVfjp1CtMtqc4KxD%2fmrFhOFIbMgPKwKqNT2oNK65hgeatkwZJrWdnm%2fMaG1OObPG4rd2lDI%2b4C%2fwVzKHYQzC70sbvr0ipQqXMoUHc%3d
Analysis Result:
 Based on the call transcript, here are the determinations:

1. **Billable Call Determination:**
    - The call is **Billable**.
    - None of the conditions (a through f) for a non-billable call apply.

2. **Final Expense Application Determination:**
   - Yes, an application was submitted during the call.
   - Customer provided necessary information for the application submission.

3. **Application Details:**
   - a. **Monthly Premium:** $63.35
   - b. **Insurance Carrier:** Aetna
   - c. **Coverage Amount:** $20,000
   - d. **Policy Type:**
       - This detail is not explicitly stated in the transcript, but no adverse health conditions were mentioned by the customer. Therefore, it would likely be **Level**.
   - e. **Was the policy declined?** No, the policy was not declined. The application was approved.

4. **Quote Provided Determination:** Not Applicable, as an application was submitted.

5. **Abrupt Ending to the Phone Call Determination:**
   - a. **Did the call end abruptly?** No, the call did not end abruptly.

All information seems consistent with a thorough completion of the insurance application process.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=P7O4CMCvAsVuz0toV1DJAtj01QiAD2zs1%2fnHYeahXXKuysRwK0ZvBoc9YvOPfhXqGvhNEqlh5WsUbYYEZpB3HUfRubYfSACvyWTT2XXhTRxb8SvzWkA581vNKx4e7Wd5k0RRdtpmq4R9tOTTFMpDrfrthBrwAhwdNul0DdxgdIiIEtct2VvTrmSyIcqhFwIQWWPR4dQaqAcR7aAd68haUHcL1d0I5%2feM5oZM10p%2fa8KFgFSxYdMrW9WbKyAgRZ4wkLrgM5MzOEs6UCQe68wzaKogpbw%3d
Analysis Result:
 ### 1. Billable Call Determination:

**Billable Status:** Billable

**Reasoning:**
- The customer does not reside in a nursing home.
- The customer has not been diagnosed with COPD.
- The customer did not explicitly state they do not have an active payment method.
- The customer does not require a power of attorney for financial decisions.
- The customer is aware that the call is about final expense or life insurance.
- The customer is not on the call solely to waste the agent's time or as a prank.

### 2. Final Expense Application Determination:

**Application Submission Status:** Not Submitted

**Reasoning:**
- The customer did not provide any of the following: checking account number, savings account number, debit card number, or credit card number.

### 3. Quote Provided Determination:

**Details of the Quote Offered by the Agent:**
- **Monthly Premium:** $24.50
- **Insurance Carrier:** Aetna
- **Coverage Amount:** $5,000
- **Policy Type:** Level
- **Reason for not purchasing the policy:** N/A (The call ended without submitting an application)
- **Was a follow-up set?** No

### 4. Abrupt Ending to the Phone Call Determination:

**Call Abruptly Ended:** Yes

**Details:**
- **1.** Were medical questions already answered? Yes (e.g., smoking status was discussed)
- **2.** Did the customer already agree to a coverage amount and monthly premium? Yes ($5,000 coverage for $24.50/month)
- **3.** Did the customer already choose a beneficiary? No
- **4.** Did the customer already give a social security number? No
- **5.** Did the customer already provide their bank account routing and account numbers OR a credit card number? No
- **6.** What was the last question asked before the call ended abruptly? The agent was confirming the dog's behavior and the customer's telephone number.

In summary, the call is billable, and an application was not submitted. The quote provided was for $5,000 coverage at a monthly premium of $24.50 with Aetna (Level policy). A follow-up was not explicitly set, and the call ended abruptly without collecting sensitive financial information.
---------------------------------------------------
Processing: https://media.ringba.com/recording-public?v=v1&k=FWwnjaUMJ17%2bECXz6%2bB1dXVQLPtO50yK4TacaXQVVssj20uyI%2fPEl0RGkQ8QvP2NnyxQrLdo7WN%2bTH7qWXktZ0emjR89d2n369O4vt62Fj3BabaaC44RdeoxJVkeL6PK6Fwn7deo2URE0UbAmJFUX%2bK6iqWhdjwJojA0FPlRh%2biQdjuxHd9%2ffgmxOyX2ZiVyeEW9Hh64oFRFg9j34zAPHlavVTPAw0zTUp%2fsJb2aQQz4IneNm5XBKg9At97cBl3wxbBoOxTrWhuEgh%2fXxSwT7%2fQn1h8%3d
Analysis Result:
 ### Call Analysis:

**1. Billable Call Determination:**
- The call is **Billable**. None of the negative conditions are met:
  - The customer does not reside in a nursing home.
  - The customer has not been diagnosed with COPD.
  - The customer does not indicate a lack of an active payment method.
  - The customer does not require a power of attorney for financial decisions.
  - The customer is aware that the call is about final expense or life insurance.
  - The customer is not wasting the agent's time or calling as a prank.

**2. Final Expense Application Determination:**
- An application was **not** submitted during the call. The customer did not provide any checking account numbers, savings account numbers, debit card numbers, or credit card numbers.

**3. If an application was submitted, provide:**
- **N/A** as no application was submitted.

**4. Quote Provided Determination:**
- **a. Monthly Premium:** $80.94.
- **b. Insurance Carrier:** Aetna.
- **c. Coverage Amount:** $10,000.
- **d. Policy Type:** Level (based on good health).
- **e. Reason for not purchasing the policy:** The customer needed to consult with her daughter who handles her financial matters.
- **f. Was a follow-up set?** Yes, a follow-up was set for the next day around 2-3 PM.

**5. Abrupt Ending to the Phone Call Determination:**
- **a. Did the call end abruptly?** No, the call did not end abruptly. The call ended with a clear agreement to follow up after the customer's daughter is consulted.

### Summary:
- The call meets the criteria for being billable.
- No application was submitted during the call.
- A follow-up is scheduled for the next day to assist the customer further.
"""

# Define a regex pattern to capture all required fields
call_pattern = re.compile(r"""
    Processing:\s(?P<recording>https://media.ringba.com/recording-public\?v=v1&k=.*)
    .+?Billable Call:\s(?P<billable>Yes|No)
    .+?Application Submitted:\s(?P<app>Yes|No)
    .+?Monthly Premium:\s\$(?P<monthly_premium>\d+\.\d+)
    .+?Insurance Carrier:\s(?P<insurance_carrier>.+)
    .+?Coverage Amount:\s\$(?P<coverage_amount>\d+,\d+)
    .+?Policy Type:\s(?P<policy_type>.+)
    .+?Reason for not purchasing:\s(?P<no_purchase_reason>.+)
    .+?Follow-up set:\s(?P<follow_up_set>Yes|No|.+)
""", re.VERBOSE | re.DOTALL)

# Find all matches in the call summaries
matches = call_pattern.finditer(call_summaries)

# Extract the data into a list of dictionaries
extracted_data = []
for match in matches:
    extracted_data.append(match.groupdict())

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(extracted_data)

# Load the existing data from the Excel file
file_path = '/mnt/data/stats.xlsx'
existing_data = pd.read_excel(file_path, sheet_name='Sheet1')

# Append the new data
updated_data = pd.concat([existing_data, df], ignore_index=True)

# Save the updated data back to the Excel file
updated_data.to_excel(file_path, index=False)

print(f"Data successfully extracted and saved to {file_path}")
