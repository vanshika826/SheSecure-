from kivymd.app import MDApp 
from kivy.lang import Builder 
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget, IconLeftWidget, IconRightWidgetWithoutTouch, IconLeftWidgetWithoutTouch
from kivymd.uix.screen import MDScreen
from kivy.utils import platform
import sqlite3
import re
from plyer import call, gps, sms, notification

class LoginScreen(MDScreen):
    def sign_in(self):
        username = self.ids.username.text
        password = self.ids.password.text

        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''
        SELECT * FROM testtb WHERE username=? AND password=?'''
        cur.execute(query, (username, password))
        result=cur.fetchone()

        if result is None or not username or not password:
            retry= MDFlatButton(text="Retry", on_press=self.close_retry)
            self.dialog = MDDialog(title = "Error", text = "Invalid Username or Password", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        else:
            self.username=username
            self.manager.get_screen("Home").useracc(username)
            self.manager.current="Home"
            self.manager.transition.direction="left"

    def close_retry(self, obj):
        self.dialog.dismiss()

class SignUpScreen(MDScreen):
    def insert_data(self):
        username = self.ids.username.text
        email = self.ids.email.text
        password = self.ids.password.text
        cfmpassword = self.ids.cfmpassword.text

        if not username or not email or not password or not cfmpassword:
            retry= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Please fill in all the details", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        elif password!=cfmpassword:
            retry= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Password and Confirm Password do not match", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        elif len(password)<8:
            retry= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Password must contain 8 characters", 
                                   size_hint = (0.7,0.2), buttons=[retry])
            self.dialog.open()
        elif not self.is_valid_email(email):
            close= MDFlatButton(text="Retry", on_press=self.close1)
            self.dialog = MDDialog(title = "Error", text = "Invalid Email", size_hint = (0.7,0.2), buttons=[close])
            self.dialog.open()
        else:
            self.username = username
            self.email = email
            self.password = password

            con = sqlite3.connect("testdb.db")
            cur = con.cursor()
            insert_query = '''
            INSERT INTO testtb VALUES (?, ?, ?)
            
        '''
            cur.execute(insert_query, (username, email, password))
            con.commit()
            con.close()

            self.manager.current="Home"
            self.manager.transition.direction="left"

    def close1(self, obj):
        self.dialog.dismiss()

    def is_valid_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
    
class Content(MDBoxLayout):
    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = "120dp"

        self.c_name = MDTextField(hint_text="Name")
        self.c_no = MDTextField(hint_text="Phone Number")

        self.add_widget(self.c_name)
        self.add_widget(self.c_no)

    def get_name_value(self):
        return self.c_name.text

    def get_phone_value(self):
        return self.c_no.text
    
class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        self.hometab()

    def useracc(self, username):
        self.username = username 

    def delete(self):
        dialog = MDDialog(
            title='Delete Account',
            text='Are you sure you want to delete your account?',
            buttons=[MDFlatButton(text='Yes', on_release=self.on_yes),
                MDFlatButton(text='No', on_press=lambda x: dialog.dismiss())])
        dialog.open()
        self.dialog=dialog
    
    def on_yes(self, obj): 
        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''DELETE FROM testtb WHERE username=?'''
        cur.execute(query, (self.username,))
        con.commit()
        con.close()

        self.dialog.dismiss()

        self.manager.current="Login" 
        self.manager.transition.direction="left"

    def contact(self):
        dialog = MDDialog(
            title="Add Emergency Number",
            type="custom",
            content_cls=Content(),
            buttons=[MDFlatButton(text='Add', on_press=self.add_contact),
                MDFlatButton(text='Cancel', on_press=lambda x: dialog.dismiss())])
        dialog.open()
        self.dialog=dialog
    
    def add_contact(self, obj):
        c_name = self.dialog.content_cls.get_name_value()
        c_no = self.dialog.content_cls.get_phone_value()
        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''INSERT INTO contacts VALUES (?, ?, ?)'''
        cur.execute(query, (self.username, c_name, c_no))
        con.commit()
        con.close()

        self.dialog.dismiss()
        self.display_contacts()

    def hometab(self):
        self.layout2=MDGridLayout(cols=1, pos_hint={"center_y":0.3}, spacing=100)
        self.layout2.bind(minimum_height=self.layout2.setter('height'))
      
        sublayout1=MDGridLayout(rows=1, padding=10,spacing=20,size_hint=(None,None),)
        sublayout1.bind(minimum_width=sublayout1.setter('width'))
        self.scroll_view1 = MDScrollView(do_scroll_x=True, do_scroll_y=False,size_hint=(1,None),size=(200,250))

        helpline_no={"Police":"100", "Ambulance":"108", "Women Helpline":"1091", "NCW":"011-26942369", "Domestic Violence Helpline":"181", "Anti-Obscene Calls Cell":"1096"}

        for key, value in helpline_no.items():
            self.card2=MDCard(size_hint=(None,None),size=("150dp","100dp"), md_bg_color="#EA3680")
            card_layout = MDFloatLayout(pos_hint={"center_y": 0.33})
            contact=MDLabel(text=key,font_size="30sp", halign="center", pos_hint={"center_x":0.5,"center_y":0.85})
            contactno=MDLabel(text=value, halign="center", pos_hint={"center_x":0.5,"center_y":0.5})
            call=MDIconButton(icon="phone", pos_hint={"center_x":0.85,"center_y":0.5}, on_press=lambda x, key=key, value=value: self.call_confirm(key, value))
            card_layout.add_widget(call)
            card_layout.add_widget(contact)
            card_layout.add_widget(contactno)
            self.card2.add_widget(card_layout)
            sublayout1.add_widget(self.card2)

        self.scroll_view1.minimum_width = sublayout1.width

        self.scroll_view1.add_widget(sublayout1)
        self.layout2.add_widget(self.scroll_view1)   

        self.sublayout3=MDGridLayout(rows=1, size_hint=(None, None),spacing=20, padding=10)
        self.sublayout3.bind(minimum_width=self.sublayout3.setter('width'),)
        self.scroll_view2 = MDScrollView(do_scroll_x=True, do_scroll_y=False,size_hint=(1,None),size=(200,200))

        locations={"Police Station":"police-station", "Pharmacy":"hospital-box", "Hospital":"hospital-building", "Bus Stop":"bus-stop"}

        for key2, value2 in locations.items():
            self.card1=MDCard(size_hint=(None,None),size=("150dp","100dp"), md_bg_color="#EA3680", on_press=lambda x, key2=key2: self.current_location(key2))
            card_layout2 = MDFloatLayout(pos_hint={"center_y": 0.33})
            loc=MDLabel(text=key2, font_size="30sp", halign="center", pos_hint = {"center_x":0.5, "center_y":0.8})
            loc_icon=MDIconButton(icon=value2, icon_size="30sp", pos_hint={"center_x":0.5,"center_y":0.4}, on_press=lambda x, key2=key2: self.current_location(key2))
            card_layout2.add_widget(loc)
            card_layout2.add_widget(loc_icon)
            self.card1.add_widget(card_layout2)
            self.sublayout3.add_widget(self.card1)

        self.scroll_view2.minimum_width = self.sublayout3.width

        self.scroll_view2.add_widget(self.sublayout3)
        self.layout2.add_widget(self.scroll_view2)
        
        self.add_widget(self.layout2)

        self.label1=MDLabel(text="Emergency contacts", font_size="40sp", halign="center", pos_hint={"center_x":0.23, "center_y":0.85}, bold=True)
        self.label2=MDLabel(text="Nearby Locations", font_size="40sp", halign="center", pos_hint={"center_x":0.2, "center_y":0.6}, bold=True)
        self.add_widget(self.label1)
        self.add_widget(self.label2)

        self.label3=MDLabel(text="Send SMS", font_size="40sp", halign="center", pos_hint={"center_x":0.13, "center_y":0.35}, bold=True)
        self.add_widget(self.label3)
        self.card3=MDCard(size_hint=(None,None),size=("100dp","100dp"), md_bg_color="##EA3680", pos_hint={"center_x":0.2, "center_y":0.2}, on_press=self.select_no)
        sms=MDIconButton(icon="message-text", icon_size="50sp", pos_hint={"center_x":0.5, "center_y":0.5}, halign="center", on_press=self.select_no)
        self.card3.add_widget(sms)
        self.add_widget(self.card3)

    def call_confirm(self, key, value):
        dialog = MDDialog(
            title='Confirmation',
            text=f"Call {key}?",
            buttons=[MDFlatButton(text='Yes', on_press=lambda x: self.call_helpline(value)),
                MDFlatButton(text='No', on_press=lambda x: dialog.dismiss())])
        dialog.open()
        self.dialog=dialog

    def call_helpline(self, value):
        tel = value
        call.makecall(tel=tel)

    def current_location(self, key2):
        gps.configure(on_location=lambda **kwargs: self.on_location(key2, **kwargs))
        gps.start(minTime=1000, minDistance=0)

    def on_location(self, key2, **kwargs):
        lat = kwargs['lat']
        lon = kwargs['lon']
        self.open_google_maps(lat, lon, key2)
        gps.stop()

    def open_google_maps(self, lat, lon, key2):
        key2=key2.lower()
        key2=key2.split()
        key2="+".join(key2)
        if platform == 'android':
            maps_url = f"geo:{lat},{lon}?q={key2}"
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            intent = Intent(Intent.ACTION_VIEW, Uri.parse(maps_url))
            PythonActivity.mActivity.startActivity(intent)
        else:
            print("This feature is only available on Android devices.")

    def display_contacts(self):
        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''SELECT contact_name, contact_no from contacts where username = ?'''
        cur.execute(query, (self.username,))
        self.data=cur.fetchall()

        if hasattr(self, 'grid'):  
            self.remove_widget(self.grid)
            
        self.grid=MDGridLayout(cols=1, pos_hint={"center_y":0.4})
        if self.data:
            for i in self.data:
                contact=TwoLineAvatarIconListItem(IconRightWidget(icon="phone", on_press=lambda x, i=i: self.emergency_call(i)), 
                                                  IconLeftWidget(icon="delete", on_press=lambda x, i=i: self.delete_confirm(i)), 
                                                  text=i[0], secondary_text=i[1], on_press=lambda x, i=i: self.edit_no(i))  
                self.grid.add_widget(contact)
            self.add_widget(self.grid)
        else:
            empty=MDLabel(text="No Contacts", halign="center") 
            self.grid.add_widget(empty)
            self.add_widget(self.grid)

    def emergency_call(self, i):
        tel = i[1]
        call.makecall(tel=tel)

    def delete_confirm(self, i):
        dialog3 = MDDialog(
            title='Delete Contact',
            text=f"Are you sure you want to delete \"{i[0]}\"",
            buttons=[MDFlatButton(text='Yes', on_press=lambda x: self.delete_no(i)),
                MDFlatButton(text='No', on_press=lambda x: dialog3.dismiss())])
        dialog3.open()
        self.dialog3=dialog3

    def delete_no(self, i):
        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''DELETE FROM contacts where username=? and contact_name=? and contact_no=?'''
        cur.execute(query, (self.username, i[0], i[1]))
        con.commit()
        con.close()

        self.dialog3.dismiss()
        self.display_contacts()

    def edit_no(self, i):
        dialog4 = MDDialog(
            title="Edit Contact",
            type="custom",
            content_cls=Content3(i=i),
            buttons=[MDFlatButton(text='Save', on_press=self.save_no),
                MDFlatButton(text='Cancel', on_press=lambda x: dialog4.dismiss())])
        dialog4.open()
        self.dialog4=dialog4
    
    def save_no(self, obj):
        c_name = self.dialog4.content_cls.get_name_value()
        c_no = self.dialog4.content_cls.get_phone_value()
        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''UPDATE contacts SET contact_name = ?, contact_no = ? WHERE username = ?'''
        cur.execute(query, (c_name, c_no, self.username))
        con.commit()
        con.close()

        self.dialog4.dismiss()
        self.display_contacts()
    
    def select_no(self, obj):
        con = sqlite3.connect("testdb.db")
        cur = con.cursor()
        query = '''SELECT contact_name, contact_no from contacts where username = ?'''
        cur.execute(query, (self.username,))
        data=cur.fetchall()

        dialog2 = MDDialog(
            title="Select Contact",
            type="custom",
            content_cls=Content2(data=data),
            buttons=[MDFlatButton(text='Cancel', on_press=lambda x: dialog2.dismiss())])
        dialog2.open()
        self.dialog2=dialog2

    def home_leave(self):
        self.remove_widget(self.layout2)
        self.remove_widget(self.label1)
        self.remove_widget(self.label2)
        self.remove_widget(self.label3)
        self.remove_widget(self.card3)

    def call_leave(self):
        self.remove_widget(self.grid)

    def info1(self):
        self.manager.current="Info1"
        self.manager.transition.direction="left"

    def info2(self):
        self.manager.current="Info2"
        self.manager.transition.direction="left"

    def info3(self):
        self.manager.current="Info3"
        self.manager.transition.direction="left"

    def logout(self):
        self.manager.current="Login"
        self.manager.transition.direction="right"
        
class Info1(MDScreen):
    def on_enter(self):

        if hasattr(self, 'scroll_view'):  
            self.remove_widget(self.scroll_view)

        file=open("info1.txt")
        data=file.read()
        self.scroll_view = MDScrollView(pos_hint={"center_y": 0.4})
        info_label = MDLabel(
            text=data,
            halign="justify",
            pos_hint={"center_y": 0.2},
            padding="20dp",
            size_hint_y=None,
        )
        info_label.bind(texture_size=lambda label, size: setattr(info_label, 'height', size[1]))

        self.scroll_view.add_widget(info_label)
        self.add_widget(self.scroll_view)

    def back1(self):
        self.manager.current="Home"
        self.manager.get_screen("Home").home_leave()
        self.manager.transition.direction="right"

    def logout(self):
        self.manager.current="Login"
        self.manager.transition.direction="right"

class Info2(MDScreen):
    def on_enter(self):

        if hasattr(self, 'scroll_view'):  
            self.remove_widget(self.scroll_view)

        file=open("info2.txt")
        data=file.read()
        self.scroll_view = MDScrollView(pos_hint={"center_y": 0.4})
        info_label = MDLabel(
            text=data,
            halign="justify",
            pos_hint={"center_y": 0.2},
            padding="20dp",
            size_hint_y=None,
        )
        info_label.bind(texture_size=lambda label, size: setattr(info_label, 'height', size[1]))

        self.scroll_view.add_widget(info_label)
        self.add_widget(self.scroll_view)

    def back2(self):
        self.manager.current="Home"
        self.manager.get_screen("Home").home_leave()
        self.manager.transition.direction="right"

    def logout(self):
        self.manager.current="Login"
        self.manager.transition.direction="right"

class Info3(MDScreen):
    def on_enter(self):

        if hasattr(self, 'scroll_view'):  
            self.remove_widget(self.scroll_view)

        file=open("info3.txt")
        data=file.read()
        self.scroll_view = MDScrollView(pos_hint={"center_y": 0.4})
        info_label = MDLabel(
            text=data,
            halign="justify",
            pos_hint={"center_y": 0.2},
            padding="20dp",
            size_hint_y=None,
        )
        info_label.bind(texture_size=lambda label, size: setattr(info_label, 'height', size[1]))

        self.scroll_view.add_widget(info_label)
        self.add_widget(self.scroll_view)
    
    def back3(self):
        self.manager.current="Home"
        self.manager.get_screen("Home").home_leave()
        self.manager.transition.direction="right"

    def logout(self):
        self.manager.current="Login"
        self.manager.transition.direction="right"

class AboutApp(MDScreen):
    def on_enter(self):
        about="SheRakshit is an extensive women's security app designed to provide a robust set of features aimed at ensuring the safety and well-being of women in various situations. With a user-friendly interface, the app combines essential resources, real-time location services, and emergency contact functionalities to create an integral safety net for its users. SheSecure commits to women’s safety. It promotes “feel free to feel safe.”  By combining essential features all together at one place, it stands as a friend for women, making her feel confident and secure every day."
        app_label = MDLabel(
            text=about,
            halign="justify",
            pos_hint={"center_y": 0.7},
            padding="20dp",
            size_hint_y=None,
        )
        app_label.bind(texture_size=lambda label, size: setattr(app_label, 'height', size[1]))
        self.add_widget(app_label)

    def back(self):
        self.manager.current="Home"
        self.manager.get_screen("Home").home_leave()
        self.manager.transition.direction="right"
    
class Content2(MDBoxLayout):
    def __init__(self, data, **kwargs):
        super(Content2, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        height = len(data) * 80
        self.height = f"{height}dp"

        for i in data:
            x = TwoLineAvatarIconListItem(
                IconRightWidgetWithoutTouch(icon="message-text"), 
                IconLeftWidgetWithoutTouch(icon="account"), 
                text=i[0], 
                secondary_text=i[1], 
                on_press=lambda x, i=i: self.liveloc(i))
            
            self.add_widget(x)

    def liveloc(self, i):
        gps.configure(on_location=lambda **kwargs: self.on_location(i, **kwargs))
        gps.start(minTime=1000, minDistance=0)

    def on_location(self, i, **kwargs):
        latitude = kwargs.get('lat', 0.0)
        longitude = kwargs.get('lon', 0.0)
        self.send_location_sms(latitude, longitude, i)
        gps.stop()

    def send_location_sms(self, latitude, longitude, i):
        recipient = i[1]
        message = f"Help! I am in danger! My current location: https://maps.google.com/maps?q={latitude},{longitude}"
        sms.send(recipient=recipient, message=message)
        title = "Message Sent!"
        text = f"Message sent to {recipient} with location information."
        notification.notify(title=title, message=text)
        
class Content3(MDBoxLayout):
    def __init__(self, i, **kwargs):
        super(Content3, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = "120dp"

        self.c_name = MDTextField(hint_text="Edit Name", text=i[0])
        self.c_no = MDTextField(hint_text="Edit Phone Number", text=i[1])

        self.add_widget(self.c_name)
        self.add_widget(self.c_no)

    def get_name_value(self):
        return self.c_name.text

    def get_phone_value(self):
        return self.c_no.text
    
class WsApp(MDApp):
    def build(self):
        self.icon="logo2.png"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette= "Pink"
        return Builder.load_file('main.kv')

if __name__=='__main__':
    WsApp().run()