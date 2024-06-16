from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi import HTTPException
from pydantic import BaseModel
from database import get_db
from bson.objectid import ObjectId
from typing import List
import csv
import os

app = FastAPI()

class OperationCreate(BaseModel):
    expression_infix: str

class OperationResponse(BaseModel):
    id: str
    expression_infix: str
    expression_postfix: str
    result: int

def precedence(op):
    if op in ('+', '-'):
        return 1
    if op in ('*', '/'):
        return 2
    return 0

def validate_expression(expression):
    # Vérifier si l'expression est vide
    if not expression:
        raise HTTPException(status_code=400, detail="Expression is empty")

    # Vérifier les parenthèses équilibrées
    pile = []
    for char in expression:
        if char == '(':
            pile.append(char)
        elif char == ')':
            if not pile:
                raise HTTPException(status_code=400, detail="Mismatched parentheses")
            pile.pop()
    if pile:
        raise HTTPException(status_code=400, detail="Mismatched parentheses")

    # Vérifier les opérateurs consécutifs et les caractères invalides
    valid_chars = set("0123456789+-*/()")
    prev_char = ''
    for char in expression:
        if char not in valid_chars:
            raise HTTPException(status_code=400, detail=f"Invalid character '{char}' in expression")
        if char in "+-*/" and (prev_char in "+-*/" or prev_char == '('):
            raise HTTPException(status_code=400, detail="Consecutive operators are not allowed")
        if char == ")" and prev_char == '(':
            raise HTTPException(status_code=400, detail="Empty parentheses")
        if char.isdigit() and prev_char == ')':
            raise HTTPException(status_code=400, detail="Missing operator between number and closing parenthesis")
        prev_char = char

def infix_to_postfix(expression):
    expression = expression.replace(" ", "")  # Supprimer les espaces
    validate_expression(expression)  # Validation de l'expression
    pile_in = []
    pile_out = []
    i = 0
    while i < len(expression):
        if expression[i].isdigit():
            num = expression[i]
            while i + 1 < len(expression) and expression[i + 1].isdigit():
                i += 1
                num += expression[i]
            pile_out.append(num)
        elif expression[i] == '(':
            pile_in.append(expression[i])
        elif expression[i] == ')':
            while pile_in and pile_in[-1] != '(':
                pile_out.append(pile_in.pop())
            pile_in.pop()
        else:
            while pile_in and precedence(pile_in[-1]) >= precedence(expression[i]):
                pile_out.append(pile_in.pop())
            pile_in.append(expression[i])
        i += 1
    while pile_in:
        pile_out.append(pile_in.pop())
    return ' '.join(pile_out)

def evaluate_postfix(expression):
    pile_in = []
    for char in expression.split():
        if char.isdigit():
            pile_in.append(int(char))
        else:
            b = pile_in.pop()
            a = pile_in.pop()
            if char == '+':
                pile_in.append(a + b)
            elif char == '-':
                pile_in.append(a - b)
            elif char == '*':
                pile_in.append(a * b)
            elif char == '/':
                pile_in.append(a / b)
    return pile_in[0]

@app.post("/calculate/", response_model=OperationResponse)
def create_operation(operation: OperationCreate, db = Depends(get_db)):
    expression_infix = operation.expression_infix
    expression_postfix = infix_to_postfix(expression_infix)
    result = evaluate_postfix(expression_postfix)
    
    operation_data = {
        "expression_infix": expression_infix,
        "expression_postfix": expression_postfix,
        "result": result
    }
    
    operation_id = db.operations.insert_one(operation_data).inserted_id
    
    created_operation = db.operations.find_one({"_id": ObjectId(operation_id)})
    
    return {
        "id": str(created_operation["_id"]),
        "expression_infix": created_operation["expression_infix"],
        "expression_postfix": created_operation["expression_postfix"],
        "result": created_operation["result"]
    }

@app.get("/operations/", response_model=List[OperationResponse])
def get_operations(db = Depends(get_db)):
    operations = db.operations.find()
    operations_list = []
    for operation in operations:
        operations_list.append({
            "id": str(operation["_id"]),
            "expression_infix": operation["expression_infix"],
            "expression_postfix": operation["expression_postfix"],
            "result": operation["result"]
        })
    return operations_list

@app.get("/download-operations/")
def download_operations(db = Depends(get_db)):
    operations = db.operations.find()
    file_path = "operations.csv"

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "expression_infix", "expression_postfix", "result"])
        for operation in operations:
            writer.writerow([
                str(operation["_id"]),
                operation["expression_infix"],
                operation["expression_postfix"],
                operation["result"]
            ])

    return FileResponse(path=file_path, filename=file_path, media_type='text/csv')
