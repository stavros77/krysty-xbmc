import xbmcgui
import common

class LoginDialog(xbmcgui.WindowXMLDialog):
    LOGIN_BUTTON = 200
    CANCEL_BUTTON = 201
    HEADER_LABEL = 100
    ACTION_PREVIOUS_MENU = 10
    ACTION_BACK = 92
    CENTER_Y = 6
    CENTER_X = 2

    _fields = [
        ('email', 30, 105, 30, 450, 0),
        ('password', 30, 185, 30, 450, 1)
    ]
    
    def __new__(cls):
        return super(LoginDialog, cls).__new__(cls, 'LoginDialog.xml', common.addon_path, 'Default', '720p')

    def __init__(self):
        super(LoginDialog, self).__init__()

    def onInit(self):
        self.query_controls = []
        
        for field in self._fields:
            control = xbmcgui.ControlEdit(0, 0, 0, 0, '',
                font='font12',
                textColor='0xFFFFFFFF',
                focusTexture='button-focus2.png',
                noFocusTexture='button-nofocus.png',
                _alignment=self.CENTER_Y | self.CENTER_X,
                isPassword=field[5]
            )
            control.setPosition(field[1], field[2])
            control.setHeight(field[3])
            control.setWidth(field[4])
            
            self.addControl(control)
            self.query_controls.append(control)
        
        self.getControl(self.HEADER_LABEL).setLabel('LOGIN')
        
        loginBtn = self.getControl(self.LOGIN_BUTTON)
        cancelBtn = self.getControl(self.CANCEL_BUTTON)
        
        self.query_controls[0].controlDown(self.query_controls[1])
        self.query_controls[1].controlUp(self.query_controls[0])
        self.query_controls[1].controlDown(loginBtn)
        loginBtn.controlUp(self.query_controls[1])
        loginBtn.controlRight(cancelBtn)
        cancelBtn.controlLeft(loginBtn)
        
        self.setFocus(self.query_controls[0])

    def onAction(self, action):
        if (action == self.ACTION_PREVIOUS_MENU) or (action == self.ACTION_BACK):
            self.close()

    def onClick(self, control):
        self.flag = False
        
        if control == self.LOGIN_BUTTON:
            for control in self.query_controls:
                if control.getText().strip() == '':
                    xbmcgui.Dialog().ok('LOGIN', 'Date insuficiente.')
                    return
            self.flag = True
            self.close()
            
        elif control == self.CANCEL_BUTTON:
            self.close()

    def onControl(self, control):
        pass

    def onFocus(self, control):
        pass

    def get_query(self):
        if self.flag:
            texts = []
            for control in self.query_controls:
                if isinstance(control, xbmcgui.ControlEdit):
                    texts.append(control.getText())
                elif isinstance(control, xbmcgui.ControlList):
                    texts.append(control.getSelectedItem().getLabel())

            params = [field[0] for field in self._fields]
            query = dict(zip(params, texts))
            return query
        return None
