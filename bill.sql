
--Generated Bills
WITH Customers AS(
SELECT c.ID AS CustomerID, c.CustomerName,  ct.CustomerType, c.Arrears AS CustomerArrears, CASE WHEN ct.CustomerType = 'Practitioner' THEN '3-PARTY' ELSE lg.LGAName END AS CustomerLGA, CASE WHEN ct.CustomerType = 'Practitioner' THEN '3P' ELSE lg.LGACode END AS LGACode--, st.[Status]
FROM [K2].[SmartBoxData].[SAuto_CustomerDetails_SMO] c
INNER JOIN [K2].[SmartBoxData].[SAuto_CustomerType_SMO] ct ON c.CustomerTypeID = ct.ID
LEFT JOIN [K2].[SmartBoxData].[SAuto_Localgovernment_SMO] lg ON c.LocalGovernmentArea = lg.ID
LEFT JOIN [K2].[SmartBoxData].[SAuto_StatusList_SMO] st ON c.CustomerStatus = st.ID
--WHERE ct.CustomerType IN ('Business Owner', 'Practitioner')
WHERE c.ID NOT IN (39474, 39472, 356845, 356860, 356863, 356939, 356940, 356946, 356947, 55957) ---112181
GROUP BY c.ID, c.CustomerName, ct.CustomerType, c.Arrears, lg.LGAName, lg.LGACode, st.[Status]),

Applications AS(
SELECT fs.ID AS RequestId, fs.RequestTitle, fs.CustomerID, fs.SignageCategory, fs.SubmissionDate, fs.StartDate, fs.EndDate, f.EndDate AS StructureEndDate, fs.TotalCost, CASE WHEN fs.RequestTitle LIKE '%Renewal Request-2024%' THEN 'Renewal' WHEN YEAR(fs.SubmissionDate) = 2024 AND YEAR(f.EndDate) = 2024 OR fs.RequestTitle NOT LIKE '%Renewal Request-2024%' THEN 'New Applications' ELSE 'Other Year' END AS [Application Type]
FROM [K2].[SmartBoxData].[SAuto_FirstParty_Signage_SMO] fs
INNER JOIN [K2].[SmartBoxData].[SAuto_FirstParty_SignageList_SMO] f ON fs.ID = f.FirstPartyRequestID
LEFT JOIN [K2].[SmartBoxData].[SAuto_StatusList_SMO] st ON fs.StatusID = st.ID
WHERE YEAR(f.EndDate) = 2024
AND fs.SignageCategory IN (1,2)
--AND fs.RequestTitle LIKE '%Renewal Request-2024%'
AND st.Status IN ('HOD Review', 'Printing and Verifying Billing Files', 'Customer Payment', 'Approved')
AND fs.CustomerID NOT IN (39474, 39472, 356845, 356860, 356863, 356939, 356940, 356946, 356947, 55957)
GROUP BY fs.ID, fs.CustomerID, fs.RequestTitle, fs.SignageCategory, fs.SubmissionDate, fs.StartDate, fs.EndDate, f.EndDate, fs.TotalCost),


BillsGeneratedOnce AS
(SELECT MaxBills.BillID, MaxBills.RequestId, b.LegalFee, b.TotalSignageCost, b.TotalArrears, b.FinalAmount, b.Timestamp
FROM
	(SELECT MAX(b.ID) AS BillID, b.RequestId
	FROM  [K2].[SmartBoxData].[BillAmounts] b 
	WHERE YEAR(TimeStamp) IN (2023, 2024)
	GROUP BY b.RequestId)MaxBills
INNER JOIN [K2].[SmartBoxData].[BillAmounts] b ON MaxBills.BillID = b.ID)
--HAVING COUNT(b.RequestId) < 2)

SELECT Customers.CustomerID, Customers.CustomerName, Customers.CustomerType, Customers.LGACode, Customers.CustomerLGA, Customers.CustomerArrears, BillsGeneratedOnce.RequestId, BillsGeneratedOnce.LegalFee, Applications.TotalCost, BillsGeneratedOnce.TotalSignageCost, BillsGeneratedOnce.TotalArrears, BillsGeneratedOnce.FinalAmount, Applications.RequestTitle, Applications.SubmissionDate, Applications.StartDate, Applications.EndDate, BillsGeneratedOnce.Timestamp, Applications.[Application Type]
FROM Customers
INNER JOIN Applications ON Customers.CustomerID = Applications.CustomerID
LEFT JOIN BillsGeneratedOnce ON Applications.RequestId = BillsGeneratedOnce.RequestId
--WHERE RenewalApplications.RequestTitle NOT LIKE '%Renewal Request-2024%'
GROUP BY Customers.CustomerID, Customers.CustomerName, Customers.CustomerType, Customers.LGACode, Customers.CustomerLGA, Customers.CustomerArrears, BillsGeneratedOnce.RequestId, BillsGeneratedOnce.LegalFee, Applications.TotalCost, BillsGeneratedOnce.TotalSignageCost, BillsGeneratedOnce.TotalArrears, BillsGeneratedOnce.FinalAmount, Applications.RequestTitle, Applications.SubmissionDate, Applications.StartDate, Applications.EndDate, BillsGeneratedOnce.Timestamp, Applications.[Application Type]
ORDER BY Customers.CustomerID
