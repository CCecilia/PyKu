sub init()
    m.top.panelSize = "medium"
    m.top.focusable = true
    m.top.hasNextPanel = true
    m.top.leftOnly = true
    m.top.createNextPanelOnItemFocus = false
    m.top.selectButtonMovesPanelForward = true
    m.top.optionsAvailable = false
    m.top.overhangTitle = m.overhangTitle
    m.top.list = m.top.findNode("MenuLabelList")
end sub
