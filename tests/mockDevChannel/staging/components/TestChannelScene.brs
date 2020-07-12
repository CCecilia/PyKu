sub init()
    ? "test channel init"
    m.top.backgroundURI = "pkg:/images/bg.jpg"
    m.categoriespanel = m.top.panelSet.createChild("LeftMenuListPanel")
end sub

function onKeyEvent(key as String, press as Boolean) as Boolean
    ? "onKeyEvent |", key, press
    if press then
        if key = "back"
            ? "back press"
        end if
    end if

    return false
end function