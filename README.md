Tai web servisas, skirtas sandėlių ir jų inventoriaus valdymui naudojant Redis duomenų bazę. Jis leidžia registruoti, gauti informaciją, atnaujinti ir ištrinti sandėlius bei jų inventorių.
Programos veikimas apsaugotas nuo vartotojo klaidingų įvesčių.

## Programos paleidimas
Vienas iš būdų paleisti programą naudojant Docker Desktop:
* Atsisiųskite ir susidiekite Docker Desktop
* Pasileiskite Docker konteinerį:
docker run -p 6379:6379 -d redis

Servisui išbandyti galima naudoti Postman programą.
## Programos aprašymas
### **Sandėlių valdymas:**

Registravimas (PUT /warehouse) – įrašo naują sandėlį į sistemą pagal unikalų ID, adresą ir plotą.

Gavimo informacija (GET /warehouse/<warehouseId>) – grąžina informaciją apie konkretų sandėlį.

Pašalinimas (DELETE /warehouse/<warehouseId>) – ištrina sandėlį ir visą jame esantį inventorių.

### **Inventoriaus valdymas:**

PUT /warehouse/<warehouseId>/inventory – prideda naują inventorių prie sandėlio.

GET /warehouse/<warehouseId>/inventory – grąžina visų sandėlyje esančių inventorių ID sąrašą.

GET /warehouse/<warehouseId>/inventory/<inventoryId> – grąžina konkretaus inventoriaus kiekį.

POST /warehouse/<warehouseId>/inventory/<inventoryId> – keičia konkretaus inventoriaus kiekį nauja verte.

POST /warehouse/<warehouseId>/inventory/<inventoryId>/change – padidina arba sumažina inventoriaus kiekį n vienetų.

DELETE /warehouse/<warehouseId>/inventory/<inventoryId> – pašalina konkretų inventorių.

### **Pagalbinės funkcijos:**
POST /flushall – pašalina visus įrašus iš Redis duomenų bazės.
