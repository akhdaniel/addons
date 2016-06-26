import pymysql.cursors


class spc(object):
    
    connection = False

    def connect(self, host='localhost', user='root', passwd='', db=''):
        self.connection = pymysql.connect(host=host,
                             user=user,
                             password=passwd,
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def insert_biller_tagihan(self, data):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `tagihan` ("
            sql += "id_record_tagihan         ,"
            sql += "nomor_pembayaran          ,"
            sql += "nama                      ,"
            sql += "kode_fakultas             ,"
            sql += "nama_fakultas             ,"
            sql += "kode_prodi                ,"
            sql += "nama_prodi                ,"
            sql += "kode_periode              ,"
            sql += "nama_periode              ,"
            sql += "is_tagihan_aktif          ,"
            sql += "waktu_berlaku             ,"
            sql += "waktu_berakhir            ,"
            sql += "strata                    ,"
            sql += "angkatan                  ,"
            sql += "urutan_antrian            ,"
            sql += "total_nilai_tagihan       ,"
            #sql += "minimal_nilai_pembayaran  ,"
            #sql += "maksimal_nilai_pembayaran ,"
            sql += "nomor_induk               ,"
            sql += "pembayaran_atau_voucher   ,"
            sql += "voucher_nama              ,"
            sql += "voucher_nama_fakultas     ,"
            sql += "voucher_nama_prodi        ,"
            sql += "voucher_nama_periode      "
            sql += ") VALUES ("
            sql += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            sql += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            sql += "%s,%s)"

            cursor.execute(sql, (
                data['id_record_tagihan']         ,
                data['nomor_pembayaran']          ,
                data['nama']                      ,
                data['kode_fakultas']             ,
                data['nama_fakultas']             ,
                data['kode_prodi']                ,
                data['nama_prodi']                ,
                data['kode_periode']              ,
                data['nama_periode']              ,
                data['is_tagihan_aktif']          ,
                data['waktu_berlaku']             ,
                data['waktu_berakhir']            ,
                data['strata']                    ,
                data['angkatan']                  ,
                data['urutan_antrian']            ,
                data['total_nilai_tagihan']       ,
                #data['minimal_nilai_pembayaran']  ,
                #data['maksimal_nilai_pembayaran'] ,
                data['nomor_induk']               ,
                data['pembayaran_atau_voucher']   ,
                data['voucher_nama']              ,
                data['voucher_nama_fakultas']     ,
                data['voucher_nama_prodi']        ,
                data['voucher_nama_periode']      ,                    
            ))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self.connection.commit()

        return True


    def delete_biller_tagihan(self, data):
        with self.connection.cursor() as cursor:
            sql = "DELETE from tagihan where id_record_tagihan = %s"
            cursor.execute(sql, (data['id_record_tagihan']))
        self.connection.commit()
        return True

    def insert_biller_tagihan_detil(self, data):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO `detil_tagihan` ("
            sql += "id_record_detil_tagihan   ,"
            sql += "id_record_tagihan         ,"
            sql += "urutan_detil_tagihan      ,"
            sql += "kode_jenis_biaya          ,"
            sql += "label_jenis_biaya         ,"
            sql += "label_jenis_biaya_panjang ,"
            sql += "nilai_tagihan             "
            sql += ") VALUES ("
            sql += "%s,%s,%s,%s,%s,%s,%s)"

            cursor.execute(sql, (
                data['id_record_detil_tagihan'],   
                data['id_record_tagihan'],         
                data['urutan_detil_tagihan'],      
                data['kode_jenis_biaya'],          
                data['label_jenis_biaya'],         
                data['label_jenis_biaya_panjang'], 
                data['nilai_tagihan']                              
            ))
        self.connection.commit()
        return True

    def delete_biller_tagihan_detil(self, data):
        with self.connection.cursor() as cursor:
            sql = "DELETE from detil_tagihan where id_record_tagihan = %s and id_record_detil_tagihan=%s"
            cursor.execute(sql, (data['id_record_tagihan'] , data['id_record_detil_tagihan']))
        self.connection.commit()
        return True


    def read_ca_pembayaran(self):
        results = []
        with self.connection.cursor() as cursor:
            sql = "SELECT "
            sql += "id_record_pembayaran      ,"
            sql += "id_record_tagihan         ,"
            sql += "waktu_transaksi           ,"
            sql += "nomor_pembayaran          ,"
            sql += "kode_unik_transaksi_bank  ,"
            sql += "waktu_transaksi_bank      ,"
            sql += "kode_bank                 ,"
            sql += "kanal_bayar_bank          ,"
            sql += "kode_terminal_bank        ,"
            sql += "total_nilai_pembayaran    ,"
            sql += "status_pembayaran         ,"
            sql += "id_record_rekonsiliasi    ,"
            sql += "id_record_settlement      ,"
            sql += "billref                   ,"
            sql += "metode_pembayaran         ,"
            sql += "catatan                   ,"
            sql += "key_val_1                 ,"
            sql += "key_val_2                 ,"
            sql += "key_val_3                 ,"
            sql += "key_val_4                 ,"
            sql += "key_val_5                  "
            sql += "FROM pembayaran where key_val_1 = nomor_pembayaran and status_pembayaran=%s"
            cursor.execute(sql, (1) )
            results = cursor.fetchall()
        return results

    def set_ca_pembayaran_processed(self, id_record_pembayaran ):
        # import pdb; pdb.set_trace()
        with self.connection.cursor() as cursor:
            sql = "UPDATE pembayaran SET key_val_1='1' where id_record_pembayaran = %s"
            cursor.execute(sql, ( id_record_pembayaran ))
        self.connection.commit()
        return True        

    def close(self):
        self.connection.close()
