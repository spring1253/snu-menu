import os
import requests
import argparse
import smtplib
import time
from bs4 import BeautifulSoup
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone

def get_snu_menu(target_date=None):
    if not target_date:
        kst = timezone(timedelta(hours=9))
        target_date = datetime.now(kst).strftime('%Y-%m-%d')
    
    url = f"https://snuco.snu.ac.kr/foodmenu/?date={target_date}"
    
    for attempt in range(3):
        try:
            response = requests.get(url, verify=False, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 데이터를 담을 바구니 준비
            lunch_results = []
            dinner_results = []
            
            rows = soup.select("table tbody tr")
            
            for row in rows:
                name_tag = row.select_one("td:nth-child(1)")
                if not name_tag: continue
                cafeteria_name = name_tag.get_text(strip=True)
                
                # 1. 점심 데이터 처리 (301동, 302동 공통)
                if "301" in cafeteria_name or "302" in cafeteria_name:
                    raw_lunch = row.select_one("td:nth-child(3)").get_text("\n", strip=True)
                    if raw_lunch and "등록된" not in raw_lunch:
                        # 301동만 <TAKE-OUT> 기준으로 자르기
                        lunch_text = raw_lunch.split("<TAKE-OUT>")[0].strip() if "301" in cafeteria_name else raw_lunch.strip()
                        lunch_results.append(f"📍 {cafeteria_name}\n{lunch_text}\n")

                # 2. 저녁 데이터 처리 (302동 전용)
                if "302" in cafeteria_name:
                    raw_dinner = row.select_one("td:nth-child(4)").get_text("\n", strip=True)
                    if raw_dinner and "등록된" not in raw_dinner:
                        dinner_results.append(f"📍 {cafeteria_name}\n{raw_dinner.strip()}\n")

            # 최종 결과물 조립
            final_output = [f"📅 {target_date} 공대 식단 알림\n"]
            
            # 점심 섹션
            if lunch_results:
                final_output.append("☀️ [점심 메뉴]")
                final_output.extend(lunch_results)
                final_output.append("-" * 20)
                
            # 저녁 섹션
            if dinner_results:
                final_output.append("🌙 [저녁 메뉴]")
                final_output.extend(dinner_results)
                final_output.append("-" * 20)

            if not lunch_results and not dinner_results:
                return f"{target_date}에 운영하는 식당이 없습니다."
                
            return "\n".join(final_output)

        except Exception as e:
            if attempt < 2:
                time.sleep(5)
                continue
            return f"크롤링 중 오류 발생: {e}"

def send_email(content, date_str):
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')

    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = f"🍴 [SNU] 식단 알림 ({date_str})"
    msg['From'] = email_user
    msg['To'] = receiver_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_user, email_password)
        smtp.send_message(msg)

if __name__ == "__main__":
    # 1. 인자 파싱
    parser = argparse.ArgumentParser(description='SNU Menu Bot')
    parser.add_argument('-d', '--date', type=str, help='조회할 날짜 (YYYY-MM-DD)')
    args = parser.parse_args()

    # 2. 식단 가져오기
    menu_info = get_snu_menu(args.date)
    print(menu_info)
    
    # 3. 메일 발송 조건 (환경변수가 있고, '운영하는 식당이 없습니다'가 아닐 때만)
    if os.environ.get('EMAIL_USER'):
        # 결과 메시지에 '없습니다'가 포함되어 있지 않을 때만 발송
        if "없습니다" not in menu_info:
            display_date = args.date if args.date else datetime.now().strftime('%m/%d')
            send_email(menu_info, display_date)
            print("이메일 발송 완료!")
        else:
            print("조회된 식단이 없어 이메일을 발송하지 않습니다.")