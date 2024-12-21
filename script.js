/**
 * @NApiVersion 2.1
 * @NScriptType Restlet
 */
/* 修改后记得save和upload file，否则云端还是旧的脚本，自然仍旧报错*/


define(['N/record', 'N/format', 'N/file', 'N/encode'], function (record, format, file, encode) {
    function parseDate(dateString) {
        return format.parse({
            value: dateString,
            type: format.Type.DATE
        });
    }

    /**
    
 * @param{record} record
 */
    /*  () => { */
    /**
     * Defines the function that is executed when a GET request is sent to a RESTlet.
     * @param {Object} requestParams - Parameters from HTTP request URL; parameters passed as an Object (for all supported
     *     content types)
     * @returns {string | Object} HTTP response body; returns a string when request Content-Type is 'text/plain'; returns an
     *     Object when request Content-Type is 'application/json' or 'application/xml'
     * @since 2015.2
     */
    const get = (requestParams) => {
        log.debug({
            title: 'GET Request Triggered',
            details: JSON.stringify(requestParams)
        });

        return 'Successfully GET Request';

    }

    /**
     * Defines the function that is executed when a PUT request is sent to a RESTlet.
     * @param {string | Object} requestBody - The HTTP request body; request body are passed as a string when request
     *     Content-Type is 'text/plain' or parsed into an Object when request Content-Type is 'application/json' (in which case
     *     the body must be a valid JSON)
     * @returns {string | Object} HTTP response body; returns a string when request Content-Type is 'text/plain'; returns an
     *     Object when request Content-Type is 'application/json' or 'application/xml'
     * @since 2015.2
     */
    const post = (requestBody) => {
        log.debug({
            title: 'POST Triggered',
            details: JSON.stringify(requestBody)
        });

        if (requestBody.posttype == 'bill') {


            var objRecord = record.create({
                type: record.Type.VENDOR_BILL,
                isDynamic: true
            });

            objRecord.setValue({
                fieldId: 'entity',
                value: requestBody.entity
            });//vendor:V001477 STRATEGIC PUBLIC RELATIONS PTE. LTD.//6176

            var tranDate = parseDate(requestBody.trandate);
            objRecord.setValue({
                fieldId: 'trandate',
                value: tranDate
            });//date:决定了posting date的所属期间:30/11/2024

            objRecord.setValue({
                fieldId: 'tranid',
                value: requestBody.tranid
            });//reference id: test001

            objRecord.setValue({
                fieldId: 'subsidiary',
                value: requestBody.subsidiary
            });//subsidiary:2

            objRecord.setValue({
                fieldId: 'memo',
                value: requestBody.memo
            });//memo: testmemo001

            /*  objRecord.setValue({
                 fieldId:'account',
                 value:requestBody.account
             });//account:往来科目:1302 */
            /* 
                        objRecord.setValue({
                            fieldId:'postingperiod',
                            value:requestBody.postingperiod
                        });//posting period: Nov 2024 */

            var duedate = parseDate(requestBody.duedate);
            objRecord.setValue({
                fieldId: 'duedate',
                value: duedate
            });//duedate:30/11/2024

            objRecord.setValue({
                fieldId: 'location',
                value: requestBody.location
            });//location:DCS Card Centre

            objRecord.setValue({
                fieldId: 'currency',
                value: requestBody.currency
            });//currency: SGD//1

            objRecord.setValue({
                fieldId: 'exchangerate',
                value: requestBody.exchangerate
            });//exchange rate:1

            var custbody_document_date = parseDate(requestBody.custbody_document_date);
            objRecord.setValue({
                fieldId: 'custbody_document_date',
                value: custbody_document_date
            });//document date:30/11/2024

            /* objRecord.setValue({
                fieldId:'nextapprover',
                value:requestBody.nextapprover
            });//nextapprover */

            objRecord.setValue({
                fieldId: 'custbody7',
                value: requestBody.custbody7
            });//submitted by: Jiayu Hu 

            objRecord.setValue({
                fieldId: "custbody_giropaidorpaid",
                value: requestBody.custbody_giropaidorpaid
            });//Giro paid/paid


        }
        if (requestBody.posttype == 'po') {
            var objRecord = record.create({
                type: record.Type.PURCHASE_ORDER,
                isDynamic: true
            });

            objRecord.setValue({
                fieldId: 'entity',
                value: requestBody.entity
            });//vendor:V001477 STRATEGIC PUBLIC RELATIONS PTE. LTD.//6176

            var tranDate = parseDate(requestBody.trandate);
            objRecord.setValue({
                fieldId: 'trandate',
                value: tranDate
            });//date:决定了posting date的所属期间:30/11/2024



            objRecord.setValue({
                fieldId: 'subsidiary',
                value: requestBody.subsidiary
            });//subsidiary:2

            objRecord.setValue({
                fieldId: 'memo',
                value: requestBody.memo
            });//memo: testmemo001

            objRecord.setValue({
                fieldId: 'location',
                value: requestBody.location
            });//location:DCS Card Centre

            objRecord.setValue({
                fieldId: 'currency',
                value: requestBody.currency
            });//currency: SGD//1

            objRecord.setValue({
                fieldId: 'exchangerate',
                value: requestBody.exchangerate
            });//exchange rate:1

            objRecord.setValue({
                fieldId: 'custbody7',
                value: requestBody.custbody7
            });//submitted by: Jiayu Hu 






        }
        if (requestBody.posttype == 'polinkedbill') {
            var objRecord = record.transform({
                fromType: record.Type.PURCHASE_ORDER,
                fromId: requestBody.fromId,//423283动态生成po number和internal id，自己记下来
                toType: record.Type.VENDOR_BILL,
                isDynamic: true
            });

            /*  objRecord.setValue({
                 fieldId: 'entity',
                 value: requestBody.entity
             });//vendor:V001477 STRATEGIC PUBLIC RELATIONS PTE. LTD.//6176 */

            /*  var tranDate = parseDate(requestBody.trandate);
             objRecord.setValue({
                 fieldId: 'trandate',
                 value: tranDate
             });//date:决定了posting date的所属期间:30/11/2024 */

            objRecord.setValue({
                fieldId: 'tranid',
                value: requestBody.tranid
            });//reference id: test001

            /*  objRecord.setValue({
                 fieldId: 'subsidiary',
                 value: requestBody.subsidiary
             });//subsidiary:2 */

            /* objRecord.setValue({
                fieldId: 'memo',
                value: requestBody.memo
            });//memo: testmemo001 */

            var duedate = parseDate(requestBody.duedate);
            objRecord.setValue({
                fieldId: 'duedate',
                value: duedate
            });//duedate:30/11/2024

            /*  objRecord.setValue({
                 fieldId: 'location',
                 value: requestBody.location
             });//location:DCS Card Centre */

            /* objRecord.setValue({
                fieldId: 'currency',
                value: requestBody.currency
            });//currency: SGD//1 */

            /* objRecord.setValue({
                fieldId: 'exchangerate',
                value: requestBody.exchangerate
            });//exchange rate:1 */

            var custbody_document_date = parseDate(requestBody.custbody_document_date);
            objRecord.setValue({
                fieldId: 'custbody_document_date',
                value: custbody_document_date
            });//document date:30/11/2024

            /* objRecord.setValue({
                fieldId:'approvalstatus',
                value:1
            });//pending approval

            objRecord.setValue({
                fieldId:'nextapprover',
                value:6542
            });//David */


            objRecord.setValue({
                fieldId: 'custbody7',
                value: requestBody.custbody7
            });//submitted by: Jiayu Hu 

            objRecord.setValue({
                fieldId: "custbody_giropaidorpaid",
                value: requestBody.custbody_giropaidorpaid
            });//Giro paid/paid


            //bill里面才有orderline id 遍历
            //po里面叫line，expense 1 和 2 ： line 也是1，2，item 1 和 2：line是 3 和 4
            //lark里面要有line的字段
            //会带过来4行，然后判断，不是的就delete
            //CurrentRecord.removeLine(options)





        }
        if (requestBody.posttype == 'bill' || requestBody.posttype == 'po') {
            requestBody.sublist.forEach(function (sublistitem) {
                //要分情况，expense，item，
                if (sublistitem.sublistitemtype == 'expense') {
                    objRecord.selectNewLine({
                        sublistId: 'expense'
                    });

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'account',
                        value: sublistitem.account
                        //564
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'department',
                        value: sublistitem.department
                        //16
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'memo',
                        value: sublistitem.memo
                        //'line description test'
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'amount',
                        value: sublistitem.amount
                        //1
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'taxcode',
                        value: sublistitem.taxcode
                        //'SG-GST 9% Purchase'//486
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'taxrate',
                        value: sublistitem.taxrate
                        //'9%'
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'taxamount',
                        value: sublistitem.taxamount
                        //0.09
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'grossamount',
                        value: sublistitem.grossamount
                        //1.09
                    })
                    objRecord.commitLine({
                        sublistId: 'expense'
                    });
                }
                if (sublistitem.sublistitemtype == 'item') {
                    objRecord.selectNewLine({
                        sublistId: 'item'
                    });

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'item',
                        value: sublistitem.item
                        //505:Acquisition Gift-CATERPILLAR 24" luggage
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'description',
                        value: sublistitem.description
                        //'test item description'
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'department',
                        value: sublistitem.department
                        //16
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'quantity',
                        value: sublistitem.quantity
                        //0
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'units',
                        value: sublistitem.units
                        //1:EA
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'rate',
                        value: sublistitem.rate
                        //0
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'amount',
                        value: sublistitem.amount
                        //0
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'taxcode',
                        value: sublistitem.taxcode
                        //486
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'taxrate',
                        value: sublistitem.taxrate
                        //'9%'
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'taxamount',
                        value: sublistitem.taxamount
                        //0
                    })

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'grossamount',
                        value: sublistitem.grossamount
                        //0
                    })


                    objRecord.commitLine({
                        sublistId: 'item'
                    });
                }

                //You must enter at least one line item for this transaction
                //前端语言（逻辑）
            })
        }
        //如果一个po产生好几个bill呢？？？
        //因为要transform，所以一定一样的
        var recordId = objRecord.save();
        if (requestBody.posttype == 'po') {
            var id = record.submitFields({
                type: record.Type.PURCHASE_ORDER,
                id: recordId,
                values: {
                    tranid: requestBody.tranid,
                    nextapprover: 6542,//David
                    approvalstatus: 2,


                },
                options: {
                    enableSourcing: false,
                    ignoreMandatoryFields: true
                }
            });

        }
        if (requestBody.posttype == 'bill' || requestBody.posttype == 'polinkedbill') {
            var id = record.submitFields({
                type: record.Type.VENDOR_BILL,
                id: recordId,
                values: {
                    approvalstatus: 1,
                    nextapprover: 6542,//David
                    /*  custbody_approval_delegate:4095,//Yancy Dong */

                },
                options: {
                    enableSourcing: false,
                    ignoreMandatoryFields: true
                }
            });

        }
        /*  objRecord.setValue({
             fieldId: 'tranid',
             value: requestBody.tranid
         });//reference id: test001 */

        /*  var recordId = objRecord.save(); */
        /* return JSON.stringify({
            id: recordId + '+' + id,
            message: 'Created successfully'
        }); */

        var decodeddata
        var fileObj
        var fileId
        requestBody.attachment.forEach(function (attachmentitem) {
            //pdf等应该属于这一类
            if (attachmentitem.type == 'png') {
                fileObj = file.create({
                    name: attachmentitem.title,
                    fileType: file.Type.PNGIMAGE,
                    contents: attachmentitem.encodeData,//decodeddata
                    //You attempted to write non-binary data into a binary file 'testpic.png' of type 'PNGIMAGE'. Binary data must be encoded as base64 strings. 
                });

                fileObj.folder = 13363;//document - file - suitescript
                fileObj.name = attachmentitem.title,
                fileId = fileObj.save();
                log.audit("fileId", fileId);
                if (requestBody.posttype == 'bill' || requestBody.posttype == 'polinkedbill') {
                    record.attach({ record: { type: 'file', id: fileId }, to: { type: record.Type.VENDOR_BILL, id: recordId } });  //later use return id
                }
                if (requestBody.posttype == 'po') {
                    record.attach({ record: { type: 'file', id: fileId }, to: { type: record.Type.PURCHASE_ORDER, id: recordId } });  //later use return id
                }
            }
            if (attachmentitem.type == 'txt') {
                // var base64data = JSON.stringify(requestBody.attachment); 
                // FAILED_TO_DECODE_STRING_ENCODED_BINARY_DATA_USING_1_ENCODING
                //"attachment":"IlTDg8aSw4LCqXN0IFN0cmnDg8aSw4LCsWcgSW5wdXQi",
                //"SGVsbG8gSmlheXU="
                function convertStringToDifferentEncoding() {
                    decodeddata = encode.convert({
                        string: attachmentitem.encodeData,
                        inputEncoding: encode.Encoding.BASE_64,
                        outputEncoding: encode.Encoding.UTF_8
                    });
                }
                convertStringToDifferentEncoding();
                //call function



                fileObj = file.create({
                    name: attachmentitem.title,
                    fileType: file.Type.PLAINTEXT,
                    contents: decodeddata
                });

                fileObj.folder = 13363;//document - file - suitescript
                fileObj.name =  attachmentitem.title,
                fileId = fileObj.save();
                log.audit("fileId", fileId);
                if (requestBody.posttype == 'bill' || requestBody.posttype == 'polinkedbill') {
                    record.attach({ record: { type: 'file', id: fileId }, to: { type: record.Type.VENDOR_BILL, id: recordId } });  //later use return id
                }
                if (requestBody.posttype == 'po') {
                    record.attach({ record: { type: 'file', id: fileId }, to: { type: record.Type.PURCHASE_ORDER, id: recordId } });  //later use return id
                }
            }


        })





        return JSON.stringify({
            //id: fileId,// belong to last file attached 
            id: recordId + '+' + id,
            message: "Created successfully"
        });
        //"message": "Created successfully\"TÃƒÂ©st StriÃƒÂ±g Input\""
        //"message": "Created successfullyHello Jiayu"


    }

    /**
     * Defines the function that is executed when a POST request is sent to a RESTlet.
     * @param {string | Object} requestBody - The HTTP request body; request body is passed as a string when request
     *     Content-Type is 'text/plain' or parsed into an Object when request Content-Type is 'application/json' (in which case
     *     the body must be a valid JSON)
     * @returns {string | Object} HTTP response body; returns a string when request Content-Type is 'text/plain'; returns an
     *     Object when request Content-Type is 'application/json' or 'application/xml'
     * @since 2015.2
     */
    const put = (requestBody) => {

    }

    /**
     * Defines the function that is executed when a DELETE request is sent to a RESTlet.
     * @param {Object} requestParams - Parameters from HTTP request URL; parameters are passed as an Object (for all supported
     *     content types)
     * @returns {string | Object} HTTP response body; returns a string when request Content-Type is 'text/plain'; returns an
     *     Object when request Content-Type is 'application/json' or 'application/xml'
     * @since 2015.2
     */
    const doDelete = (requestParams) => {

    }

    return { get, put, post, delete: doDelete }


});
