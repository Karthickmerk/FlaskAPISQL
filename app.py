from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/k_test'
db = SQLAlchemy(app)


# Model
class Candidate(db.Model):
    __tablename__ = "candidate"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    email = db.Column(db.String(30))
    test_score = relationship("Test_score", uselist=False, back_populates="candidate")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"{self.id}"
class Test_score(db.Model):
    __tablename__ = "test_score"
    id = db.Column(db.Integer, primary_key=True)
    first_round = db.Column(db.Integer)
    second_round = db.Column(db.Integer)
    third_round = db.Column(db.Integer)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'))
    candidate = relationship("Candidate", back_populates="test_score")

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, first_round, second_round,third_round):
        self.first_round = first_round
        self.second_round = second_round
        self.third_round = third_round

    def __repr__(self):
        return f"{self.id}"

db.create_all()


class AllCandiateMarks(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Candidate
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    Test_score =  fields.List(fields.Number())
    print('------------------------------------')
    print(type(Test_score))
    print(Test_score)


# Get Candidates Score

@app.route('/api/allcandidates', methods=['GET'])
def index():
    get_candidates = Candidate.query.all()
    todo_schema = AllCandiateMarks(many=True)
    candidates = todo_schema.dump(get_candidates)
    return make_response(jsonify({"Candidates": candidates}))


@app.route('/api/allcandidates/<id>', methods=['GET'])
def get_todo_by_id(id):
    get_todo = Candidate.query.get(id)
    todo_schema = AllCandiateMarks()
    todo = todo_schema.dump(get_todo)
    return make_response(jsonify({"todo": todo}))


@app.route('/api/allcandidates/<id>', methods=['PUT'])
def update_candidate_by_id(id):
    data = request.get_json()
    get_todo = Candidate.query.get(id)
    if data.get('name'):
        get_todo.name = data['name']
    if data.get('email'):
        get_todo.email = data['email']
    db.session.add(get_todo)
    db.session.commit()
    todo_schema = AllCandiateMarks(only=['id', 'name', 'email'])
    todo = todo_schema.dump(get_todo)
    return make_response(jsonify({"todo": todo}))


@app.route('/api/allcandidates/<id>', methods=['DELETE'])
def delete_candidate_by_id(id):
    get_candidate = Candidate.query.get(id)
    db.session.delete(get_candidate)
    db.session.commit()
    return make_response("", 204)


@app.route('/api/allcandidates', methods=['POST'])
def create_newcandidate():
    data = request.get_json()
    candidate_schema = AllCandiateMarks()
    candidate = candidate_schema.load(data)
    result = candidate_schema.dump(candidate.create())
    return make_response(jsonify({"New Candidate": result}), 200)


if __name__ == "__main__":
    app.run(debug=True)
