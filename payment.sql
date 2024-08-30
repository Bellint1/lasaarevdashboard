WITH Customers AS(
SELECT c.ID AS CustomerID, c.CustomerName,  ct.CustomerType,  lg.LGAName AS OldCustomerLGA, 
		CASE WHEN ct.CustomerType = 'Practitioner' THEN '3-PARTY' ELSE lg.LGAName END AS CustomerLGA,
		lg.LGACode--, st.[Status]
FROM [K2].[SmartBoxData].[SAuto_CustomerDetails_SMO] c
LEFT JOIN [K2].[SmartBoxData].[SAuto_CustomerType_SMO] ct ON c.CustomerTypeID = ct.ID
LEFT JOIN [K2].[SmartBoxData].[SAuto_Localgovernment_SMO] lg ON c.LocalGovernmentArea = lg.ID
LEFT JOIN [K2].[SmartBoxData].[SAuto_StatusList_SMO] st ON c.CustomerStatus = st.ID
--WHERE ct.CustomerType IN ('Business Owner', 'Practitioner')
WHERE c.ID NOT IN (39474, 39472, 356845, 356860, 356863, 356939, 356940, 356946, 356947, 55957) ---112181
GROUP BY c.ID, c.CustomerName, ct.CustomerType, lg.LGAName, lg.LGACode, st.[Status]),

CustomerPayments AS(
SELECT prt.Reference_No AS Receipt_Number
      ,p.CustomerID
      ,p.PaymentFor
      ,p.TxtRef AS TxtRef
      ,p.AmountRequested
      ,p.AmountPaid
      ,p.RequestStatus
      ,p.TimeStamp
      ,p.TellerNumber
      ,p.PaymentDate
	  ,YEAR(p.PaymentDate) AS PaymentYear
	  ,FORMAT(p.PaymentDate, 'MMMM') AS PaymentMonth
      ,p.ApprovedDate

FROM [K2].[SmartBoxData].[SAuto_Payment_SMO] p
LEFT JOIN [K2].[SmartBoxData].[SAuto_PaymentReceipt_SMO] prt ON p.ID = prt.Payment_ID
WHERE p.PaymentFor IN ('Arrears Part Payment', 'Payment on Account')
AND p.RequestStatus = 'Approved'
--AND p.TellerNumber LIKE '%SMALL FORMAT%'
AND p.CustomerID NOT IN (39474, 39472, 356845, 356860, 356863, 356939, 356940, 356946, 356947, 55957)
AND YEAR(p.PaymentDate) = 2024
AND YEAR(p.ApprovedDate) = 2024)
SELECT  Customers.CustomerID, Customers.CustomerName, Customers.CustomerType, CASE WHEN CustomerPayments.TxtRef LIKE '%-INS-%' THEN 'INSTITUTION' ELSE  Customers.CustomerLGA End AS CustomerLGA, 
		CASE WHEN CustomerPayments.TxtRef LIKE '%-INS-%' THEN 'INS' WHEN Customers.CustomerType = 'Practitioner' THEN '3P' ELSE Customers.LGACode End AS LGACode, 
		CustomerPayments.*
FROM Customers
INNER JOIN CustomerPayments ON Customers.CustomerID = CustomerPayments.CustomerID