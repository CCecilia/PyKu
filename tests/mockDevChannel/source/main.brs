sub Main()
    screen = CreateObject("roSGScreen")
    m.port = CreateObject("roMessagePort")
    screen.setMessagePort(m.port)
    scene = screen.CreateScene("TestChannelScene")

    m.global = screen.getGlobalNode()
    m.global.addFields({
        "environment": CONST__ENV
        "useDebug": CONST__USE_DEBUG
        "someCountConst": CONST_INT
        "overhangTitle": CONST_SCENE_TITLE
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