import requests
from requests.exceptions import HTTPError
import os
from datetime import date, timedelta

UPCOMING_SUNDAY = (date.today() - timedelta(days=date.today().weekday()+1)) + timedelta(weeks=1)

BULLETIN_DATA = {
    'date': '2022-12-04',
    'hymns': [
        { 'num': 335, 'title': 'All hail the power (CORONATION)' },
        { 'num': 354, 'title': 'Come, ye souls by sin afflicted' },
        { 'num': 233, 'title': 'I to the hills will lift mine eyes' },
        { 'num': 80, 'title': 'I waited for the LORD' },
        { 'num': 722, 'title': 'Sanctus (Schubert)' },
        { 'num': 499, 'title': 'How sweet and awful is the place' },
        { 'num': 44, 'title': 'The King of Love my Shepherd Is' },
        { 'num': 269, 'title': 'psalm 134' } ],
  'scripture': 'Revelation 5:12-13',
  'preacher': 'Jason Cherry',
  'confessionVerse': 'Revelation 3:2-3',
  'assuranceVerse': 'Isaiah 12:2',
  'oldTestamentReading': '2 Chronicles 34:1--10',
  'newTestamentReading': 'James 4:1--10',
  'creed': 'Nicene',
  'benediction': 'Now the God of peace, that brought again from the dead our Lord Jesus, that great shepherd of the sheep, through the blood of the everlasting covenant, make you perfect in every good work to do his will, working in you that which is well-pleasing in his sight, through Jesus Christ; to whom be glory for ever and ever. Amen. Hebrews 13:20,21',
  'collect': 'Almighty and merciful God, it is only by your gift that your faithful people offer you true and laudable service: Grant that we may run without stumbling to obtain your heavenly promises; through Jesus Christ our Lord, who lives and reigns with you and the Holy Spirit, one God, now and for ever.',
  'newMembers': '',
  'baptisms': ''
}


def send(data, download_filename=None):
    try:
        resp = requests.get('http://127.0.0.1:9090', json=data)
        resp.raise_for_status()

        if (download_filename is not None):
            os.makedirs('downloads', exist_ok=True)
            with open(f'downloads/{download_filename}', 'wb') as fd:
                for chunk in resp.iter_content(chunk_size=128):
                    fd.write(chunk)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')

if __name__ == "__main__":
    send(BULLETIN_DATA, "bulletin.pdf")
