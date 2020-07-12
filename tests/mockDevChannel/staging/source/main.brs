sub Main()
    screen = CreateObject("roSGScreen")
    m.port = CreateObject("roMessagePort")
    screen.setMessagePort(m.port)
    scene = screen.CreateScene("TestChannelScene")

    m.global = screen.getGlobalNode()
    m.global.addFields({
        "environment": "prod"
        "useDebug": true
        "someCountConst": 123
        "overhangTitle": "PyKu Test Channel"
    })

    screen.show()

    while(true)
        msg = wait(0, m.port)
        msgType = type(msg)

        if msgType = "roSGScreenEvent"
            if msg.isScreenClosed() then return
        end if
    end while
end sub