SELECT c.ID AS CustomerID, c.CustomerName, c.Arrears AS CustomerArrears, ct.CustomerType,  lg.LGAName AS OldCustomerLGA, 
		CASE WHEN ct.CustomerType = 'Practitioner' THEN '3-PARTY' ELSE lg.LGAName END AS CustomerLGA,
		lg.LGACode
FROM [K2].[SmartBoxData].[SAuto_CustomerDetails_SMO] c
INNER JOIN [K2].[SmartBoxData].[SAuto_CustomerType_SMO] ct ON c.CustomerTypeID = ct.ID
INNER JOIN [K2].[SmartBoxData].[SAuto_Localgovernment_SMO] lg ON c.LocalGovernmentArea = lg.ID
LEFT JOIN [K2].[SmartBoxData].[SAuto_StatusList_SMO] st ON c.CustomerStatus = st.ID
WHERE c.ID NOT IN (39474, 39472, 356845, 356860, 356863, 356939, 356940, 356946, 356947, 55957)---112181
GROUP BY c.ID, c.CustomerName, c.Arrears, ct.CustomerType, lg.LGAName, lg.LGACode, st.[Status]