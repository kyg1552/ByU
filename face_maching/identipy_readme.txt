<개요>
idenipy는 3개의 python 파일로 구성되어있고, 특정인물을 사진에서 찾아내여 일치율을 보여주는 프로그램이다.

먼저, args_group_generator.py 를 실행하여 학습시킬 인물(들)의 사진url, 그룹이름, 사진의 정보를 등록하여
학습그룹을 형성한다.

그 다음 args_learning_check.py 를 통해 그룹에 등록된 이미지의 학습완료 여부를 확인한다.

마지막 args_faceid_match.py 에서 학습시킨 그룹명, 비교할 사진의 url을 입력해 인물정보를 매칭한다.

python 파일 실행시, 아규먼트를 적용시켰기 때문에 접속어를 사용해 값을 넣을수있다.


<사용법>
파일 실행시 아규먼트 접속어를 사용해 값을 입력할수있다. 접속어를 모를때는 python "파일명" -h 를 이용해 정보를 
얻을 수 있다.



1.args_group_generator.py (-g '그룹명' , -n '사진명', -u'사진속 학습자 정보', -i '학습이미지의 url')

generator는 4개의 정보를 받아야한다. 위의 4개중 '그룹명', '사진명', '사진속 학습자 정보'를 입력하지않을경우
에러가 발생하여, 그룹이 생성되지않는다.

'이미지 url'을 입력하지않으면, default로 지정된 학습이미지가 지정된다.('./face_api_train_cp.jpg')

이 파일을 사용해 생성된 그룹명은 중복될수없으며, 그룹은 24시간후 삭제되므로 24시간후 같은 그룹명을 재사용가능하다.

*예시 : python args_group_generator.py -g'test_group' -n'tom' -u'VIP' -i './tom_pic.jpg'






2. args_learning_check.py (-g '그룹명')

args_learning_check.py는 1개의 입력정보를 받아서 학습상황을 보여준다.

정보를 입력하지 않을경우 에러가 발생한다.
학습이 완료되었을경우 success를 반환한다.

*예시 : python args_learning_check.py -g 'test_group'





3. args_faceid_match.py (-g'그룹명' , -i'비교할 사진 url')

args_faceid_match.py는 학습된 그룹과 사진을 비교하여, 사진내에 학습된 사람을 찾아낸다.

-g '그룹명' 에 학습시킨 그룹을 입력하고

-i '비교할 사진의 url' 에 비교사진의 로컬주소를 입력한다.

그룹명을 입력하지않을 경우 에러가 발생하며, 이미지를 입력하지않을경우 default이미지 경로가 입력된다.

*예시 : python args_faceid_match.py -g 'test_group' -i './image_test.jpg'





