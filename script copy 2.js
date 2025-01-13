/**
 * @NApiVersion 2.1
 * @NScriptType Restlet
 */
/* 修改后记得save和upload file，否则云端还是旧的脚本，自然仍旧报错*/


define(['N/record', 'N/format', 'N/file', 'N/encode','N/search'], function (record, format, file, encode, search) {
    function parseDate(dateString) {
        return format.parse({
            value: dateString,
            type: format.Type.DATE
        });
    }

    /**
 * 检查指定单据类型是否存在相同的 tranid
 * @param {string} recordType - 例如 record.Type.PURCHASE_ORDER 或 record.Type.VENDOR_BILL
 * @param {string} tranid - 前端传入的 tranid
 * @returns {boolean} 如果重复，返回 true；否则返回 false
 */
    function isTranIdDuplicated(recordType, tranid) {
        // 如果前端没传 tranid，视为不重复
        if (!tranid) return false;

        var duplicateSearch = search.create({
            type: recordType,
            filters: [
                ['tranid', 'is', tranid],
                'AND',
                ['mainline', 'is', 'T']
            ],
            columns: ['internalid']
        });

        var sr = duplicateSearch.run().getRange({ start: 0, end: 1 });
        return (sr && sr.length > 0);
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
        // var tranid = requestBody.tranid;
        // var tranidSearch = search.create({
        //     type: record.Type.PURCHASE_ORDER,
        //     filters: [
        //         ['tranid', 'is', tranid]
        //     ],
        //     columns: ['internalid']
        // });

        // var searchResult = tranidSearch.run().getRange({ start: 0, end: 1 });
        // if (searchResult.length > 0) {
        //     // 如果找到重复的tranid，返回错误信息
        //     return JSON.stringify({
        //         success: false,
        //         message: 'Duplicate tranid detected. The tranid already exists.'
        //     });
        // }
        if (requestBody.posttype == 'po') {
            // ========== 检查重复 ==========
            if (isTranIdDuplicated(record.Type.PURCHASE_ORDER, requestBody.tranid)) {
                return JSON.stringify({
                    success: false,
                    message: 'Duplicate tranid detected for Purchase Order. The tranid already exists: ' + requestBody.tranid
                });
            }
        // ========== 无重复则继续创建 PO ==========
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
                fieldId: "custbody_ml_billcreatefromlark",
                value: true
            });//auto approved
            
            
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

                   /*  objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'taxrate',
                        value: sublistitem.taxrate
                        //'9%'
                    }) */

                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'tax1amt',
                        value: sublistitem.taxamount
                        //0.09
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'cseg_business',
                        value: sublistitem.cseg_business
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'cseg_scheme',
                        value: sublistitem.cseg_scheme
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'cseg_pr_type',
                        value: sublistitem.cseg_pr_type
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'class',
                        value: sublistitem.class
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'cseg1',
                        value: sublistitem.cseg1
                        //'9%'
                    })

                   /*   objRecord.setCurrentSublistValue({
                        sublistId: 'expense',
                        fieldId: 'grossamt',
                        value: sublistitem.grossamount
                        //1.09
                    })  */
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

                  
                    
/* 
                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'taxrate',
                        value: sublistitem.taxrate
                        //'9%'
                    }) */

                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'tax1amt',
                        value: sublistitem.taxamount
                        //0
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'cseg_business',
                        value: sublistitem.cseg_business
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'cseg_scheme',
                        value: sublistitem.cseg_scheme
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'cseg_pr_type',
                        value: sublistitem.cseg_pr_type
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'class',
                        value: sublistitem.class
                        //'9%'
                    })
                    objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'cseg1',
                        value: sublistitem.cseg1
                        //'9%'
                    })

                   /*  objRecord.setCurrentSublistValue({
                        sublistId: 'item',
                        fieldId: 'grossamt',
                        value: sublistitem.grossamount
                        //0
                    }) */


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
                    nextapprover: 4095,//Yanxi
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
                    nextapprover: 4095,//Yanxi
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
            var fileExtension = attachmentitem.type.toLowerCase().replace(/^\./, '');
            switch (fileExtension) {
                case 'png':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.PNGIMAGE,
                        contents: attachmentitem.encodeData, // Base64 编码的 PNG 数据
                    });
                    break;
                
                case 'pdf':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.PDF,
                        contents: attachmentitem.encodeData, // Base64 编码的 PDF 数据
                    });
                    break;
                
                case 'jpg':
                case 'jpeg':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.JPGIMAGE,
                        contents: attachmentitem.encodeData, // Base64 编码的 JPG 数据
                    });
                    break;
                
                case 'gif':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.GIFIMAGE,
                        contents: attachmentitem.encodeData, // Base64 编码的 GIF 数据
                    });
                    break;
                
                case 'tiff':
                case 'tif':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.TIFFIMAGE,
                        contents: attachmentitem.encodeData, // Base64 编码的 TIFF 数据
                    });
                    break;
                
                case 'bmp':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.BMPIMAGE,
                        contents: attachmentitem.encodeData, // Base64 编码的 BMP 数据
                    });
                    break;
                
                case 'doc':
                case 'docx':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.WORD,
                        contents: attachmentitem.encodeData, // Base64 编码的 Word 文档
                    });
                    break;
                
                case 'xls':
                case 'xlsx':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.EXCEL,
                        contents: attachmentitem.encodeData, // Base64 编码的 Excel 文档
                    });
                    break;
                
                case 'csv':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.CSV,
                        contents: attachmentitem.encodeData, // Base64 编码的 CSV 文件
                    });
                    break;
                
                case 'html':
                case 'htm':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.HTMLDOC,
                        contents: attachmentitem.encodeData, // Base64 编码的 HTML 文件
                    });
                    break;
                
                case 'txt':
                    // 对于纯文本文件，需要进行解码处理
                    decodeddata = encode.convert({
                        string: attachmentitem.encodeData,
                        inputEncoding: encode.Encoding.BASE_64,
                        outputEncoding: encode.Encoding.UTF_8
                    });
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.PLAINTEXT,
                        contents: decodeddata // 解码后的文本内容
                    });
                    break;
                
                case 'svg':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.SVG,
                        contents: attachmentitem.encodeData, // Base64 编码的 SVG 文件
                    });
                    break;
                
                case 'zip':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.ZIP,
                        contents: attachmentitem.encodeData, // Base64 编码的 ZIP 文件
                    });
                    break;
                
                case 'rtf':
                    fileObj = file.create({
                        name: attachmentitem.title,
                        fileType: file.Type.RTF,
                        contents: attachmentitem.encodeData, // Base64 编码的 RTF 文件
                    });
                    break;
                
                // 您可以根据需要继续添加更多的文件类型
                
                default:
                    log.error({
                        title: 'Unsupported File Type',
                        details: 'The file type "' + attachmentitem.type + '" is not supported.'
                    });
                    return; // 跳过不支持的文件类型
            }
        
            // 设置文件夹
            fileObj.folder = 13363; // document - file - suitescript
        
            // 保存文件
            try {
                fileId = fileObj.save();
                log.audit("fileId", fileId);
            } catch (e) {
                log.error({
                    title: 'File Save Error',
                    details: e.message
                });
                return; // 跳过保存失败的文件
            }
        
            // 附加文件到相应的记录
            try {
                if (requestBody.posttype == 'bill' || requestBody.posttype == 'polinkedbill') {
                    record.attach({
                        record: { type: 'file', id: fileId },
                        to: { type: record.Type.VENDOR_BILL, id: recordId }
                    });
                }
                
                if (requestBody.posttype == 'po') {
                    record.attach({
                        record: { type: 'file', id: fileId },
                        to: { type: record.Type.PURCHASE_ORDER, id: recordId }
                    });
                }
            } catch (e) {
                log.error({
                    title: 'File Attach Error',
                    details: e.message
                });
            }
        });





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
