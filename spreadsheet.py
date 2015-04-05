# coding: utf-8
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import gdata.spreadsheet.service
import gdata.service
import gdata.alt.appengine
import atom.service
import gdata.spreadsheet

 


class Page(webapp.RequestHandler):
    def get(self):
        try:    
            # スプレッドシートキーを設定
            spreadsheet_key = '0AtH4HuxqMDkwdExhUm5rZ1RCdnB3S1oxc0lESGpTN3c'
            # スプレッドシートを編集可能なユーザーアカウントを設定
            email = 'kemoners@gmail.com'
            # ユーザーアカウントのパスワードを設定
            password = 'diamondchair022ng0QAZX'
            # 書き込み先のシート名を設定
            # ''の前に u を付けることでユニコードに変換
            # 変換を行わない場合、エラーが発生する
            spreadsheet_name = 'tagdata'
            # 書き込み内容のリストを設定
            # ''の前に u を付けてユニコードに変換
            # 変換を行わない場合、エラーが発生する
            values = ['ID/Name' ,'pagenum' ,'parenttag' ,'tag' ,'time']
            # SpreadsheetsServiceを取得
            service = gdata.spreadsheet.service.SpreadsheetsService()
            gdata.alt.appengine.run_on_appengine(service, store_tokens=True,single_user_mode=True)
    
            # 編集に使用するユーザーアカウントの情報を設定
            service.email = email
            service.password = password
            # 設定したユーザーアカウントでログインを実行
            service.ProgrammaticLogin()
    
            # スプレッドシートIDを取得
            spreadsheet_id = self.getSpreadsheetIdByName(service, spreadsheet_key, spreadsheet_name)
    
            # ワークシートIDが取得出来なかった場合、メッセージを表示して処理を終了
            if spreadsheet_id == '':
                self.response.out.write('Spreadsheet not found.')
                return
    
            # ワークシートIDが取得できた場合、書き込み処理の実行
            self.addSpreadsheetRecord(service, spreadsheet_key, spreadsheet_id, values)
    
            self.response.out.write('success.')
            return
        except BaseException, e:
            self.response.out.write('error<br/>')
            self.response.out.write(e)
            return


def getSpreadsheetIdByName(self, service, spreadsheet_key, Spreadsheet_name):
    u'''スプレッドシートIDを取得'''

    # keyを使ってスプレッドシートを取得
    feed = service.GetWorksheetsFeed(spreadsheet_key)
    spreadsheet_entry = None
    spreadsheet_id = ''

    if not feed:
        # 取得出来なかった場合、空欄を返却
        return ''
    # スプレッドシートが取得できた場合、書き込み先のシートを取得
    for entry in feed.entry:
        # 取得したいシート名と一致した場合、そのシートを取得
        if(entry.title.text == Spreadsheet_name):
            spreadsheet_entry = entry
            break
    # 取得したシートからスプレッドシートIDを取得
    if spreadsheet_entry:
        id_parts = spreadsheet_entry.id.text.split('/')
        spreadsheet_id = id_parts[-1]
    else:
        # 取得出来なかった場合、空欄を返却
        return ''
    # 取得したスプレッドシートIDを返却
    return spreadsheet_id


def addSpreadsheetRecord(self, service, spreadsheet_key, spreadsheet_id, values):
    u'''スプレッドシートへ書き込み処理を実行'''
    try:
        data={}
        # スプレッドシートのタイトル一覧(一列目の項目)を取得
        titles = self.getSpreadsheetTitleList(service, spreadsheet_key, spreadsheet_id)

        # 書き込み内容と、タイトル一覧を対応付ける
        for i,value in enumerate(values):
            if i < len(titles):
                key = titles[i]
                data[key] = value
            else:
                break
        # スプレッドシートキー、スプレッドシートIDを使ってスプレッドシートへの書き込みを実行
        return service.InsertRow(data, spreadsheet_key, spreadsheet_id)

    except Exception, e:
        raise e



def getSpreadsheetTitleList(self, service, spreadsheet_key, spreadsheet_id):
    u'''スプレッドシートのタイトル一覧を取得'''
    first_row_contents = []
    #スプレッドシートの一行目(タイトル)を取得
    query = gdata.spreadsheet.service.CellQuery()
    query.max_row = '1'
    query.min_row = '1'
    feed = service.GetCellsFeed(spreadsheet_key, spreadsheet_id, query=query)

    # 取得できた場合、タイトルのリストを作成
    for entry in feed.entry:
        first_row_contents.append(entry.content.text)

    # タイトル一覧を格納したリストを返却
    return first_row_contents

def main():
    app = webapp2.WSGIApplication([('/.*', Page)],
                                     debug=True)
if __name__ == "__main__":
    main()
