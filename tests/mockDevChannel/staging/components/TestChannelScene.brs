sub init()
    topRef = m.top
    globalRef = m.global
    topRef.backgroundURI = "pkg:/images/bg_hd.jpg"
    m.leftMenuPanel = topRef.panelSet.createChild("LeftMenuListPanel")
    m.leftMenuPanel.setFocus(true)
    m.infoPanel = topRef.panelSet.createChild("InfoPanel")
    m.menuPanel = createObject("roSGNode", "MenuPanel")
    m.overhangTitle = Substitute("{0} | {1}", globalRef.overhangTitle,  globalRef.environment)
    m.top.overHang.title = m.overhangTitle
    m.leftMenuPanel.list.content = topRef.findNode("menuListContentNode")
    m.leftMenuPanel.list.observeField("itemFocused", "showMenuInfo")
end sub

sub showMenuInfo()
    m.menuContent = m.leftMenuPanel.list.content.getChild(m.leftMenuPanel.list.itemFocused)
    infoLabel = m.infoPanel.findNode("infoLabel")
    infoLabel.text = m.menuContent.description
    m.top.overHang.title = m.menuContent.title
    m.infoPanel.observeField("focusedChild", "showMenuPanel")
    m.leftMenuPanel.setFocus(true)
end sub

sub showMenuPanel()
    if not m.top.panelSet.isGoingBack
        if m.top.panelSet.numPanels <= 2 then m.top.panelSet.appendChild(m.menuPanel)
        menuTitle = m.menuPanel.findNode("titleLabel")
        menuDescription = m.menuPanel.findNode("descriptionLabel")
        menuTitle.text = m.menuContent.title
        menuDescription.text = m.menuContent.description
    else
        m.leftMenuPanel.setFocus(true)
    end if
end sub
