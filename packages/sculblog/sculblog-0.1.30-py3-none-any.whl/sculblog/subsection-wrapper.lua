-- subsection-wrapper.lua
-- Pandoc filter to wrap content between H1 headers in subsection divs

function Pandoc(doc)
    local new_blocks = {}
    local current_subsection = {}
    local in_subsection = false
    
    for i, block in ipairs(doc.blocks) do
        if block.t == "Header" and block.level == 1 then
            -- If we were in a subsection, close it
            if in_subsection and #current_subsection > 0 then
                local subsection_div = pandoc.Div(current_subsection, {class = "subsection"})
                table.insert(new_blocks, subsection_div)
                current_subsection = {}
            end
            
            -- Add the H1 header
            table.insert(new_blocks, block)
            
            -- Start a new subsection
            in_subsection = true
        else
            -- If we're in a subsection, collect the content
            if in_subsection then
                table.insert(current_subsection, block)
            else
                -- If no H1 has been encountered yet, just add the block
                table.insert(new_blocks, block)
            end
        end
    end
    
    -- Close the final subsection if needed
    if in_subsection and #current_subsection > 0 then
        local subsection_div = pandoc.Div(current_subsection, {class = "subsection"})
        table.insert(new_blocks, subsection_div)
    end
    
    return pandoc.Pandoc(new_blocks, doc.meta)
end

