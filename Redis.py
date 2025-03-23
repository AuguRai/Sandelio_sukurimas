import re
import redis
from flask import (Flask, request, Response)

idRegex = "^[A-Z0-9]{1,5}$"

def create_app():
    app = Flask(__name__)
    redisClient = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def warehouseKey(warehouseId):
        return f'warehouseId:{warehouseId}'
    
    def inventoryKey(warehouseId, inventoryId):
        return f'warehouseId:{warehouseId}:inventoryId:{inventoryId}'

    # Funkcija skirta įvesti sandėlį
    @app.route('/warehouse', methods=['PUT'])
    def register_warehouse():
        reqBody = request.json
        warehouseInfoValue = str(reqBody.get("adresas")) + ":" + str(reqBody.get("plotasM2")) 
        info = warehouseInfoValue.split(':')
        key = str(reqBody.get("id"))
        if redisClient.get(warehouseKey(key)) == None:
            if re.search(idRegex, key) != None:
                if info[1].isnumeric()== False:
                    return { "message": "Neteisingai įvestas sandėlio plotas"}, 401               
                else:    
                    redisClient.set(warehouseKey(key), warehouseInfoValue)
                    return { "message": "Sandėlis užregistruotas" }, 200                
            else:
                return { "message": "Sandėlio ID įvestas neteisingai"}, 402        
        else:
            return { "message": "Sandėlis tokiu ID jau užregistruotas" }, 400
          

    # Funkcija skirta gauti informaciją apie sandėlį
    @app.route('/warehouse/<warehouseId>', methods=['GET'])
    def get_warehouse_info(warehouseId):
        warehouse = redisClient.get(warehouseKey(warehouseId))

        if (warehouse != None):
            warehouseInfo = warehouse.split(':')
            return {
                "id": str(warehouseId),
                "adresas": str(warehouseInfo[0]),
                "plotasM2": int(warehouseInfo[1])
            }, 200
        else:
            return { "message": "Sandėlis nurodytu ID nerastas" }, 404
        
    # Funkcija skirta panaikinti sandėlį (taip pat panaikina ir visą sandėlyje esantį inventorių)
    @app.route('/warehouse/<warehouseId>', methods=['DELETE'])
    def delete_warehouse(warehouseId):
        if redisClient.get(warehouseKey(warehouseId)) != None:

            inventory_keys = redisClient.keys(f"warehouseId:{warehouseId}:inventoryId:*")
            for key in inventory_keys:
                redisClient.delete(key)

            redisClient.delete(warehouseKey(warehouseId))

            return { "message": "Sandėlis išregistruotas" }, 200
        else:
            return { "message": "Sandėlis nurodytu ID nerastas" }, 404

    # Funkcija skirta pridėti naują inventorių prie sandėlio
    @app.route("/warehouse/<warehouseId>/inventory", methods=['PUT'])
    def put_inventory(warehouseId):
        if redisClient.get(warehouseKey(warehouseId)) != None:
            reqBody = request.json
            inventoryInfoValue = str(reqBody.get("id")) + ":" + str(reqBody.get("amount"))
            invinfo = inventoryInfoValue.split(':')

            if redisClient.get(inventoryKey(warehouseId, invinfo[0])) == None:
 
                if int(invinfo[1]) <= 0:
                    return { "message": "Inventoriaus kiekis turi būti teigiamas skaičius" }, 400
                else:
                    redisClient.set(inventoryKey(warehouseId, invinfo[0]), invinfo[1])
                    return { "message": "Inventorius pridėtas" }, 200
            else:
                return { "message": "Inventoriaus ID jau egzistuoja" }, 400
        else:
            return { "message": "Sandėlis nurodytu ID nerastas" }, 404

    # Funkcija skirta gauti visų sandėlyje esančių inventorių pavadinimus
    @app.route('/warehouse/<warehouseId>/inventory', methods=['GET'])
    def get_inventory_info(warehouseId):
        warehouse = redisClient.get(warehouseKey(warehouseId))
        if (warehouse != None):
            lst = []
            all_keys = redisClient.keys(f"warehouseId:{warehouseId}:inventoryId:*")
            for key in all_keys:
                keyinfo = key.split(':')
                lst.append(keyinfo[3])
            return {"inventory": lst}, 200
        else:
            return { "message": "Sandėlis nurodytu ID nerastas" }, 404


    # Funkcija skirta gauti kiekį esantį inventoriuje
    @app.route('/warehouse/<warehouseId>/inventory/<inventoryId>', methods=['GET'])
    def get_inventory_quantity_info(warehouseId, inventoryId):
        inventory = redisClient.get(inventoryKey(warehouseId, inventoryId))
        if (inventory != None):
            inventoryInfo = inventory.split(':')
            value = inventoryInfo[0]
            return Response(value, status=200)
        else:
            return { "message": "Sandėlis arba inventorius nerasti" }, 404
        

    # Funkcija skirta pakeisti inventoriaus kiekį
    @app.route('/warehouse/<warehouseId>/inventory/<inventoryId>', methods=['POST'])
    def change_inventory_quantity(warehouseId, inventoryId):
        inventory = redisClient.get(inventoryKey(warehouseId, inventoryId))
        if (inventory != None):
            newValue = request.data.decode('utf-8')
            if int(newValue) <= 0:
                return { "message": "Inventoriaus kiekis turi būti teigiamas skaičius" }, 400
            else:
                redisClient.set(inventoryKey(warehouseId, inventoryId), newValue)  
                return { "message": "Inventoriaus kiekis pakeistas" }, 200 

        else:
            return { "message": "Sandėlis arba inventorius nerasti" }, 404
        

    # Funkcija skirta padidinti arba sumažinti inventoriaus kiekį n vienetų
    @app.route('/warehouse/<warehouseId>/inventory/<inventoryId>/change', methods=['POST'])
    def diff_inventory_quantity(warehouseId, inventoryId):
        inventory = redisClient.get(inventoryKey(warehouseId, inventoryId))

        if (inventory != None):
            changeValue = request.data.decode('utf-8')
            
            if(int(changeValue) != 0):
                redisClient.incrby(inventoryKey(warehouseId, inventoryId), changeValue)
                return {"message": "Sekmingai atnaujinta"}, 200           
            else:
                return {"message": "Neteisingai įvesta reikšmė"}, 400

        else:
            return { "message": "Sandėlis arba inventorius nerasti" }, 404   


    # Funkcija skirta pašalinti inventorių iš sąrašo
    @app.route('/warehouse/<warehouseId>/inventory/<inventoryId>', methods=['DELETE'])
    def delete_inventory(warehouseId, inventoryId):
        if redisClient.get(inventoryKey(warehouseId, inventoryId)) != None:
            redisClient.delete(inventoryKey(warehouseId, inventoryId))
 
            return { "message": "Inventorius pašalintas" }, 200
        else:
            return { "message": "Sandėlio arba inventoriaus nepavyko rasti" }, 404     


    @app.route('/flushall', methods=['POST'])
    def flush_all():
        redisClient.flushall()
        return { "message": "Sėkmingai panaikinta" }, 200
        

            
    return app
